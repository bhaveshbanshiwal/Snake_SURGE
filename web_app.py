import time
import math
import threading
import psutil
import os
from flask import Flask, request, jsonify, render_template, g
from src.calibrated_gait import number

from src.snake_locomotion import SnakeKinematics
from src.path_engine import PathEngine
from src.simulation_interface import SimulationInterface
from src.st3215_interface import ST3215Interface

app = Flask(__name__)

# Global State
state = {
    'is_running': False,
    'is_paused': True,
    'progress': 0.0,
    'engine': 'SIM',  # SIM, ST3215
    'status': 'Disconnected',
    'target_path': [],
    'actual_path': [],
    'telemetry': {},
    'robot_pose': {'x': 0.0, 'y': 0.0, 'yaw': 0.0},
    'segments': [],
    'params': {'fric': 20.0, 'amp': 0.8, 'freq': 2.0, 'phase': 1.0, 'force': 5.0, 'low_power': False},
    'controller': {'active': False, 'x': 0.0, 'y': 0.0, 'trigger_rt': 0.0, 'raw_buttons': {}},
    'is_reversed': False
}

active_iface = None
kinematics = SnakeKinematics()
path_engine = PathEngine()
start_time = 0

control_lock = threading.RLock()


@app.before_request
def local_control():
    if request.remote_addr not in ('127.0.0.1', '::1') or request.host.split(':')[0] not in ('127.0.0.1', 'localhost'):
        return jsonify(error='Demo controls are local to this computer'), 403
    if request.method == 'POST' and (request.headers.get('Sec-Fetch-Site') == 'cross-site' or
            request.headers.get('Origin', request.host_url.rstrip('/')) != request.host_url.rstrip('/')):
        return jsonify(error='Cross-origin control is disabled'), 403
    if request.method == 'POST' and request.endpoint not in ('start_run', 'stop_run') and not isinstance(request.get_json(silent=True), dict):
        return jsonify(error='Expected a JSON object'), 400
    control_lock.acquire()
    g.control_locked = True


@app.teardown_request
def unlock_control(error):
    if getattr(g, 'control_locked', False):
        control_lock.release()


@app.errorhandler(ValueError)
def invalid_input(error):
    return jsonify(error=str(error)), 400


def stop_motion(status='Stopped'):
    state['is_paused'] = True
    state['status'] = status
    if active_iface and state['engine'] == 'ST3215':
        active_iface.stop()


def start_motion():
    if not state['is_running']:
        raise ValueError('Connect an engine first')
    if state['engine'] != 'SIM':
        raise ValueError('Hardware motion uses tools/demo.py with the calibrated map; dashboard hardware is telemetry only')
    if len(state['target_path']) < 2 and not state['controller']['active']:
        raise ValueError('Draw a path or move the controller first')
    state['is_paused'] = False
    state['run_deadline'] = time.monotonic() + 60
    state['status'] = 'Running (60 second limit)'


def update_motion(dt):
    if not state['is_running'] or not active_iface:
        return
    if state['is_paused']:
        state['telemetry'] = active_iface.read_telemetry()
        return
    if time.monotonic() >= state['run_deadline']:
        stop_motion('Run time limit reached')
        return
    if state['controller']['active'] and time.monotonic() - state.get('controller_time', 0) > .5:
        state['controller']['active'] = False
        stop_motion('Controller lost')
        return
    rx, ry, ryaw = active_iface.get_robot_pose()
    state['robot_pose'] = dict(x=rx, y=ry, yaw=ryaw)
    state['segments'] = active_iface.get_all_segment_positions()
    if not state['actual_path'] or math.dist(state['actual_path'][-1], (rx, ry)) > .05:
        state['actual_path'].append([rx, ry])
        state['actual_path'] = state['actual_path'][-10000:]
    path = state['target_path']
    if state['controller']['active']:
        cx, cy = state['controller']['x'], state['controller']['y']
        heading = ryaw - (math.atan2(cy, cx) - math.pi / 2)
        path = [[rx, ry], [rx + math.cos(heading), ry + math.sin(heading)]]
        turn = PathEngine().calculate_pure_pursuit(rx, ry, ryaw, path)
    elif len(path) > 1:
        turn = path_engine.calculate_pure_pursuit(rx, ry, ryaw, path)
        state['progress'] = path_engine.progress(rx, ry, path)
        if state['progress'] >= .98 and math.dist((rx, ry), path[-1]) < .2:
            stop_motion('Path Complete')
            return
    else:
        stop_motion('No path')
        return
    speed = state['params'].get('speed', 1) * (.1 if state['params']['low_power'] else 1)
    state['sim_time'] = state.get('sim_time', 0) + dt * speed
    kinematics.phase_shift = state['params']['phase'] * (-1 if state['is_reversed'] else 1)
    positions, angles = kinematics.calculate_positions(state['sim_time'], turn)
    active_iface.update_physics(state['params']['fric'], 0, 1.5, [rx, ry, 0])
    active_iface.write_positions(angles, max_force=state['params']['force'], steps=max(1, min(24, round(dt * 240))))
    state['telemetry'] = active_iface.read_telemetry()


def update_loop():
    last = time.monotonic()
    while True:
        with control_lock:
            now = time.monotonic()
            try:
                update_motion(min(.1, now - last))
            except Exception as error:
                state['is_paused'] = True
                state['is_running'] = False
                state['status'] = f'Error: {error}'
                if active_iface:
                    try:
                        active_iface.disconnect()
                    except Exception as stop_error:
                        state['status'] += f'; shutdown: {stop_error}'
            last = time.monotonic()
        time.sleep(.02)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/3d')
def viewer_3d():
    return render_template('3d_viewer.html')

@app.route('/api/3d_status', methods=['GET'])
def get_3d_status():
    if active_iface and state['engine'] == 'SIM':
        return jsonify({
            'segments': active_iface.get_3d_state(),
            'target_path': state['target_path'],
            'actual_path': state['actual_path']
        })
    return jsonify({'segments': [], 'target_path': [], 'actual_path': []})

@app.route('/api/connect', methods=['POST'])
def connect_engine():
    global state, active_iface, start_time
    data = request.json
    engine_type = data.get('engine', 'SIM')
    if engine_type not in ('SIM', 'ST3215'):
        raise ValueError('Unknown engine')
    
    if state['is_running']:
        # Disconnect
        stop_motion()
        state['is_running'] = False
        if active_iface:
            active_iface.disconnect()
        state['status'] = 'Disconnected'
        return jsonify({'success': True, 'status': state['status']})
    
    # Connect
    state['engine'] = engine_type
    if engine_type == 'SIM':
        active_iface = SimulationInterface()
    elif engine_type == 'ST3215':
        port = data.get('port')
        if not isinstance(port, str) or not port.strip():
            raise ValueError('Select an explicit serial port')
        active_iface = ST3215Interface(port=port.strip())

    state['status'] = 'Connecting...'
    if engine_type == 'SIM':
        headless_flag = data.get('headless', True)
        success, msg = active_iface.connect(headless=headless_flag)
    else:
        success, msg = active_iface.connect()
    
    if success:
        state['is_running'] = True
        state['is_paused'] = True
        state['sim_time'] = 0.0
        path_engine.progress_idx = 0
        state['progress'] = 0.0
        start_time = time.time()
        state['actual_path'] = []
        state['status'] = f"Connected to {engine_type}"
    else:
        state['status'] = f"Failed: {msg}"
        
    return jsonify({'success': success, 'status': state['status']})

@app.route('/api/params', methods=['POST'])
def set_params():
    global state, kinematics
    data = request.json
    bounds = dict(fric=(1, 50), amp=(0, 1.2), freq=(.1, 5), phase=(.1, 3), force=(.1, 20), speed=(.1, 10))
    updates = {key: number(data[key], key, *limits) for key, limits in bounds.items() if key in data}
    if 'low_power' in data:
        if type(data['low_power']) is not bool:
            raise ValueError('low_power must be boolean')
        updates['low_power'] = data['low_power']
    state['params'].update(updates)

    kinematics.amplitude = state['params']['amp']
    kinematics.frequency = state['params']['freq']
    kinematics.phase_shift = state['params']['phase']
    return jsonify({'success': True})

@app.route('/api/set_path', methods=['POST'])
def set_path():
    global state
    data = request.json
    new_path = data.get('path', [])
    if not isinstance(new_path, list) or len(new_path) > 1000:
        raise ValueError('Path must have at most 1000 points')
    for point in new_path:
        if not isinstance(point, list) or len(point) != 2:
            raise ValueError('Each path point must have two coordinates')
        for value in point:
            number(value, 'coordinate', -20, 20)
    if new_path and (len(new_path) < 2 or all(point == new_path[0] for point in new_path)):
        raise ValueError('Path needs two different points')
    stop_motion('Path ready; press Start' if new_path else 'Path cleared')
    state['target_path'] = new_path
    state['actual_path'] = []
    state['progress'] = 0.
    path_engine.progress_idx = 0

    # Sync with sim if running
    if state['engine'] == 'SIM' and active_iface and state['is_running']:
        active_iface.draw_target_path(state['target_path'])
        
    return jsonify({'success': True})

@app.route('/api/status', methods=['GET'])
def get_status():
    global state
    return jsonify({
        'is_running': state['is_running'],
        'is_paused': state['is_paused'],
        'progress': state['progress'],
        'status': state['status'],
        'engine': state['engine'],
        'robot_pose': state['robot_pose'],
        'telemetry': state['telemetry'],
        'segments': state['segments'],
        'actual_path': state['actual_path'][-50:],
        'controller': state['controller'],
        'is_reversed': state['is_reversed']
    })


@app.route('/api/controller', methods=['POST'])
def handle_controller():
    global state, active_iface, start_time
    data = request.json
    
    controller = state['controller']
    x = number(data.get('stick_x', controller['x']), 'stick_x', -1, 1)
    y = number(data.get('stick_y', controller['y']), 'stick_y', -1, 1)
    rt = number(data.get('trigger_rt', controller['trigger_rt']), 'trigger_rt', 0, 1)
    controller.update(x=x, y=y, trigger_rt=rt, active=abs(x) > .25 or abs(y) > .25)
    state['controller_time'] = time.monotonic()
    if isinstance(data.get('raw_buttons'), dict):
        controller['raw_buttons'] = data['raw_buttons']
    if data.get('btn_stop'):
        stop_motion()
    elif data.get('btn_start'):
        start_motion()
    if data.get('btn_reverse'):
        state['is_reversed'] = not state['is_reversed']
    if data.get('btn_preset'):
        state['params']['amp'] = .4 if state['params']['amp'] >= .8 else .8
        kinematics.amplitude = state['params']['amp']

    return jsonify({'success': True})

@app.route('/api/system_stats', methods=['GET'])
def get_system_stats():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent
    
    temp = 0.0
    try:
        if os.path.exists('/sys/class/thermal/thermal_zone0/temp'):
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = float(f.read().strip()) / 1000.0
        else:
            temp = "N/A"
    except Exception:
        temp = "Error"
        
    return jsonify({
        'cpu': cpu,
        'ram': ram,
        'temp': temp
    })

@app.route('/api/report', methods=['GET'])
def get_report():
    target = state['target_path']
    actual = state['actual_path']
    
    if len(target) < 2 or len(actual) < 2:
        return jsonify({'error': 'Not enough data'})
        
    if state['engine'] != 'SIM':
        return jsonify(error='Hardware has no measured XY localization'), 400
    avg_error = sum(path_engine.deviation(x, y, target) for x, y in actual) / len(actual)
    accuracy_percent = max(0.0, 100.0 * (1.0 - (avg_error / 0.5)))
    
    return jsonify({
        'avg_error': avg_error,
        'progress': state['progress'],
        'source': 'illustrative simulation; score uses 0.5 m normalization',
        'accuracy_percent': accuracy_percent,
        'target_path': target,
        'actual_path': actual
    })

@app.route('/api/start', methods=['POST'])
def start_run():
    start_motion()
    return jsonify(success=True)


@app.route('/api/stop', methods=['POST'])
def stop_run():
    stop_motion()
    return jsonify(success=True)


if __name__ == '__main__':
    threading.Thread(target=update_loop, daemon=True).start()
    app.run(host='127.0.0.1', port=5000, debug=False)
