"""Finite calibrated gait trial; dry-run by default. Never opens serial on import."""
import argparse
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.calibrated_gait import load_map, targets_at, validate_gait, slew
from src.st3215_interface import ST3215Interface

PERIOD = .05
MAX_GAP = .3


def feedback(iface, bounds, clock=time.monotonic):
    started = clock()
    state = iface.read_telemetry()
    if clock() - started > MAX_GAP:
        raise RuntimeError('Telemetry deadline exceeded')
    for sid, (low, high) in bounds.items():
        row = state.get(sid, {})
        position = row.get('position')
        if not row.get('valid') or type(position) is not int or not low <= position <= high:
            raise RuntimeError(f'Joint {sid}: missing feedback or position outside permitted range')
    return state


def track(state, target, since, now, error, timeout):
    for sid, value in target.items():
        if abs(state[sid]['position'] - value) > error:
            since.setdefault(sid, now)
            if now - since[sid] >= timeout:
                raise RuntimeError(f'Joint {sid}: sustained tracking error')
        else:
            since.pop(sid, None)


def run_motion(iface, config, target_at, duration, *,
               clock=time.monotonic, sleep=time.sleep):
    """The caller owns disconnect, including failure before RUN acknowledgement."""
    bounds = {j['id']: (j['min'], j['max']) for j in config['joints']}
    state = feedback(iface, bounds, clock)
    current = {sid: float(state[sid]['position']) for sid in bounds}
    neutral = {j['id']: j['zero'] for j in config['joints']}
    iface.start()
    iface.write_positions({sid: round(v) for sid, v in current.items()}, speed=config['speed'])
    last = clock()
    started = last
    next_tick = last + PERIOD
    since = {}
    aligned = 0
    stage = 'align'
    motion_start = None
    finished = None
    while True:
        sleep(max(0, next_tick - clock()))
        now = clock()
        dt = now - last
        if dt > MAX_GAP:
            raise RuntimeError('Control deadline exceeded; stopping')
        last = now
        next_tick = now + PERIOD
        elapsed = 0 if motion_start is None else now - motion_start
        desired = neutral if stage != 'motion' else target_at(min(elapsed, duration))
        current = slew(current, desired, config['speed'], dt)
        command = {sid: round(v) for sid, v in current.items()}
        iface.write_positions(command, speed=config['speed'])
        state = feedback(iface, bounds, clock)
        track(state, command, since, clock(), config['tracking_error'], config['tracking_timeout'])
        at_neutral = all(abs(state[sid]['position'] - v) <= 15 for sid, v in neutral.items())
        if stage == 'align':
            aligned = aligned + 1 if at_neutral else 0
            if aligned >= 2:
                stage = 'motion'
                motion_start = clock()
            elif now - started > 15:
                raise TimeoutError('Calibrated neutral was not reached')
        elif stage == 'motion' and elapsed >= duration:
            stage = 'settle'
            finished = now
            aligned = 0
        elif stage == 'settle':
            aligned = aligned + 1 if at_neutral else 0
            if aligned >= 2:
                return
            if now - finished > 5:
                raise TimeoutError('Return to neutral was not confirmed')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--hardware', action='store_true', help='Explicitly enable physical motion')
    parser.add_argument('--port', help='Required for hardware; no automatic port selection')
    parser.add_argument('--gait', choices=('yaw', 'pitch', 'sidewind'), default='pitch')
    parser.add_argument('--duration', type=float, default=10)
    parser.add_argument('--amplitude', type=float, default=5, help='Degrees; default is a small commissioning trial')
    args = parser.parse_args()
    config = load_map(require_calibrated=args.hardware)
    amplitude = math.radians(args.amplitude)
    yaw = amplitude if args.gait in ('yaw', 'sidewind') else 0
    pitch = amplitude if args.gait in ('pitch', 'sidewind') else 0
    parameters = (yaw, pitch, 0, .1, math.pi / 2, math.pi / 2, args.duration, 2)
    validate_gait(config, *parameters)
    target_at = lambda t: targets_at(t, config, *parameters)
    if not args.hardware:
        frames = [target_at(i * PERIOD) for i in range(math.ceil(args.duration / PERIOD) + 1)]
        print(f'DRY RUN: {args.gait}, {len(frames)} frames, {args.duration}s; no serial port opened')
        for joint in config['joints']:
            values = [frame[joint['id']] for frame in frames]
            print(f"ID {joint['id']:2d}: {joint['axis']:5s}, sign {joint['sign']:+d}, targets {min(values)}..{max(values)}")
        return
    if not args.port:
        parser.error('--hardware requires an explicit --port')
    iface = ST3215Interface(port=args.port)
    try:
        success, message = iface.connect()
        if not success:
            raise RuntimeError(message)
        run_motion(iface, config, target_at, args.duration)
        print('Trial completed; calibrated neutral confirmed.')
    finally:
        iface.disconnect()


if __name__ == '__main__':
    main()
