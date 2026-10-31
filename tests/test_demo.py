import copy
import math
import sys
import unittest
from unittest.mock import patch

from src.calibrated_gait import load_map, validate_map, validate_gait, targets_at
from src.path_engine import PathEngine
from src.snake_locomotion import SnakeKinematics
from src.st3215_interface import ST3215Interface
from tools.demo import run_motion, feedback, track
import web_app as web


class SerialDouble:
    def __init__(self):
        self.writes = []
        self.lines = []
        self.closed = False

    def write(self, packet):
        self.writes.append(packet)
        replies = {b'RUN\n': b'OK,RUN\n', b'STOP\n': b'OK,STOP\n',
                   b'T\n': b'T,1:5:0:2048,\n'}
        if packet in replies:
            self.lines.append(replies[packet])
        return len(packet)

    def readline(self):
        return self.lines.pop(0) if self.lines else b''

    def close(self):
        self.closed = True


class CalibratedTrials(unittest.TestCase):
    def test_saved_map_and_finite_envelope(self):
        config = load_map(require_calibrated=True)
        self.assertEqual(config['speed'], 1500)
        self.assertEqual([j['sign'] for j in config['joints']], [1, 1, -1, 1, -1, 1, -1, 1, -1, 1])
        args = (math.radians(5), math.radians(5), 0, .1, math.pi / 2, math.pi / 2, 10, 2)
        validate_gait(config, *args)
        self.assertEqual(set(targets_at(0, config, *args).values()), {2048})
        self.assertEqual(set(targets_at(10, config, *args).values()), {2048})
        for t in (1, 3, 6, 9):
            self.assertTrue(all(1252 <= v <= 2844 for v in targets_at(t, config, *args).values()))
        self.assertGreater(targets_at(1, config, *args)[1], 2048)
        self.assertLess(targets_at(1, config, *args)[9], 2048)

    def test_invalid_map_and_speed_envelope(self):
        config = load_map()
        config['joints'][1]['id'] = 1
        with self.assertRaises(ValueError):
            validate_map(config)
        config = load_map()
        with self.assertRaises(ValueError):
            validate_gait(config, 1, 1, 0, .6, 1, 1, 10, 2, speed=100)

    def test_dry_run_never_opens_serial(self):
        with patch('serial.Serial', side_effect=AssertionError('must not open hardware')):
            with patch.object(sys, 'argv', ['demo', '--gait', 'sidewind']):
                with patch('builtins.print'):
                    from tools.demo import main
                    main()

    def test_hardware_cleanup_after_failed_trial(self):
        from tools.demo import main
        iface = unittest.mock.Mock()
        iface.connect.return_value = (True, 'Connected')
        with patch.object(sys, 'argv', ['demo', '--hardware', '--port', 'TEST']), \
                patch('tools.demo.ST3215Interface', return_value=iface), \
                patch('tools.demo.run_motion', side_effect=RuntimeError('feedback lost')):
            with self.assertRaisesRegex(RuntimeError, 'feedback lost'):
                main()
        iface.disconnect.assert_called_once()

    def test_finite_motion_and_feedback_failures(self):
        config = load_map()
        class Robot:
            def __init__(self):
                self.targets = {i: 2048 for i in range(1, 11)}
                self.started = False
                self.commands = []
            def read_telemetry(self):
                return {i: dict(valid=True, position=v) for i, v in self.targets.items()}
            def start(self):
                self.started = True
            def write_positions(self, targets, speed):
                self.targets = targets
                self.commands.append(targets)
        now = [1.]
        robot = Robot()
        def sleep(dt):
            now[0] += dt
        run_motion(robot, config, lambda t: {i: 2050 for i in range(1, 11)}, .2,
                   clock=lambda: now[0], sleep=sleep)
        self.assertTrue(robot.started)
        self.assertEqual(set(robot.commands[-1].values()), {2048})
        def late_sleep(dt):
            now[0] += dt + .31
        with self.assertRaisesRegex(RuntimeError, 'Control deadline'):
            run_motion(robot, config, lambda t: robot.targets, .2, clock=lambda: now[0], sleep=late_sleep)
        robot.targets.pop(4)
        with self.assertRaisesRegex(RuntimeError, 'Joint 4'):
            feedback(robot, {i: (1252, 2844) for i in range(1, 11)})
        since = {}
        track({1: dict(position=2048)}, {1: 2200}, since, 1, 100, .5)
        with self.assertRaisesRegex(RuntimeError, 'tracking error'):
            track({1: dict(position=2048)}, {1: 2200}, since, 1.6, 100, .5)


class Transport(unittest.TestCase):
    def setUp(self):
        self.iface = ST3215Interface()
        self.iface.serial_port = SerialDouble()
        self.iface.is_connected = True

    def test_explicit_arm_and_stop_on_disconnect(self):
        with self.assertRaises(RuntimeError):
            self.iface.write_positions({1: 2048})
        self.iface.start()
        self.iface.write_positions({1: 9999}, speed=400)
        port = self.iface.serial_port
        self.assertEqual(port.writes[-1], b'P,1:2844:400\n')
        self.iface.disconnect()
        self.assertEqual(port.writes[-1], b'STOP\n')
        self.assertTrue(port.closed)

    def test_targets_are_atomic_and_missing_feedback_is_not_fabricated(self):
        self.iface.start()
        count = len(self.iface.serial_port.writes)
        with self.assertRaises(ValueError):
            self.iface.write_positions({1: 2048, 11: 2048})
        self.assertEqual(len(self.iface.serial_port.writes), count)
        self.assertEqual(self.iface.last_positions, {})
        rows = self.iface.read_telemetry()
        self.assertTrue(rows[1]['valid'])
        self.assertFalse(rows[2]['valid'])
        self.assertIsNone(rows[2]['position'])

    def test_fragmented_reply_and_fault(self):
        self.iface.serial_port.lines = [b'OK,', b'RUN\n']
        self.assertEqual(self.iface._wait('OK,RUN'), 'OK,RUN')
        self.iface.serial_port.lines = [b'ERR,SERVO,ID=2\n']
        with self.assertRaises(RuntimeError):
            self.iface._wait('T,')
        self.assertFalse(self.iface.armed)


class Routes(unittest.TestCase):
    def test_undulation_progress_and_sparse_path_error(self):
        engine = PathEngine()
        path = [[i / 5, 0] for i in range(11)]
        for i in range(1, 11):
            engine.calculate_pure_pursuit(i / 5, .18, 0, path)
        self.assertAlmostEqual(engine.progress(2, 0, path), 1)
        self.assertEqual(engine.deviation(5, 0, [[0, 0], [10, 0]]), 0)
        engine = PathEngine()
        engine.calculate_pure_pursuit(0, 0, 0, [[0, 0], [2, 0], [2, 2], [0, 0]])
        self.assertEqual(engine.progress_idx, 0)

    def test_planar_simulation_and_encoder_limits_agree(self):
        gait = SnakeKinematics()
        gait.amplitude = 100
        ticks, angles = gait.calculate_positions(.4)
        for sid in ticks:
            self.assertTrue(1252 <= ticks[sid] <= 2844)
            self.assertAlmostEqual(angles[sid], (ticks[sid] - 2048) / gait.ticks_per_radian)


class Dashboard(unittest.TestCase):
    def setUp(self):
        self.saved = copy.deepcopy(web.state)
        self.iface = web.active_iface
        web.active_iface = None
        web.state.update(is_running=False, is_paused=True, target_path=[], actual_path=[], engine='SIM')
        web.path_engine.progress_idx = 0
        self.client = web.app.test_client()

    def tearDown(self):
        if web.active_iface is not self.iface and web.active_iface:
            web.active_iface.disconnect()
        web.active_iface = self.iface
        web.state.clear()
        web.state.update(self.saved)

    def test_input_limits_and_local_control(self):
        for payload in ({'path': [[0, 0], [math.nan, 0]]}, {'path': [[0, 0]]}, {'path': [[0, 0]] * 1001}):
            self.assertEqual(self.client.post('/api/set_path', json=payload).status_code, 400)
        self.assertEqual(self.client.post('/api/params', json={'amp': math.inf}).status_code, 400)
        self.assertEqual(self.client.post('/api/params', json=[]).status_code, 400)
        self.assertEqual(self.client.post('/api/stop', headers={'Origin': 'http://evil.test'}).status_code, 403)
        self.assertEqual(self.client.post('/api/stop', headers={'Host': 'evil.test'}).status_code, 403)
        self.assertEqual(self.client.get('/api/status', environ_base={'REMOTE_ADDR': '192.168.1.5'}).status_code, 403)
        self.assertEqual(self.client.post('/api/connect', json={'engine': 'unknown'}).status_code, 400)

    def test_pause_start_stop_and_runtime_limit(self):
        web.state['is_running'] = True
        self.assertEqual(self.client.post('/api/start').status_code, 400)
        self.client.post('/api/set_path', json={'path': [[0, 0], [2, 0]]})
        self.assertTrue(web.state['is_paused'])
        self.assertEqual(self.client.post('/api/start').status_code, 200)
        self.assertFalse(web.state['is_paused'])
        web.active_iface = unittest.mock.Mock()
        web.state['run_deadline'] = 0
        web.update_motion(.02)
        self.assertTrue(web.state['is_paused'])
        self.assertEqual(web.state['status'], 'Run time limit reached')
        self.assertEqual(self.client.post('/api/stop').status_code, 200)

    def test_hardware_cannot_claim_path_following(self):
        web.state.update(engine='ST3215', is_running=True, target_path=[[0, 0], [2, 0]])
        self.assertEqual(self.client.post('/api/start').status_code, 400)
        self.assertTrue(web.state['is_paused'])

    def test_controller_loss_and_report(self):
        web.state.update(is_running=True, is_paused=False, run_deadline=math.inf,
                         target_path=[[0, 0], [10, 0]], actual_path=[[1, 0], [5, 0]])
        web.state['controller']['active'] = True
        web.state['controller_time'] = 0
        web.active_iface = unittest.mock.Mock()
        web.update_motion(.02)
        self.assertEqual(web.state['status'], 'Controller lost')
        report = self.client.get('/api/report').json
        self.assertEqual(report['avg_error'], 0)
        self.assertEqual(report['accuracy_percent'], 100)

    def test_actual_pybullet_connect_tick_and_disconnect(self):
        response = self.client.post('/api/connect', json={'engine': 'SIM', 'headless': True})
        self.assertTrue(response.json['success'], response.json)
        self.assertTrue(web.state['is_paused'])
        self.client.post('/api/set_path', json={'path': [[0, 0], [2, 0]]})
        self.client.post('/api/start')
        web.update_motion(.02)
        self.assertTrue(web.state['telemetry'])
        self.assertTrue(self.client.get('/api/3d_status').json['segments'])
        self.assertTrue(self.client.post('/api/connect', json={'engine': 'SIM'}).json['success'])


if __name__ == '__main__':
    unittest.main()
