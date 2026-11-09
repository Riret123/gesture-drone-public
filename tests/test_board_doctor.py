from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from drone_bringup.doctor import COMMANDS, EXPECTED_TYPES, bounded_run, diagnose
import subprocess


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.env = {'ROS_DISTRO': 'jazzy', 'AMENT_PREFIX_PATH': '/overlay'}
        self.outputs = {
            COMMANDS['time_sync']: (0, 'yes\n'),
            COMMANDS['topics']: (0, '/mavros/state\n/flight_cmd\n/flight_cmd_ack'),
            COMMANDS['services']: (0, '/mavros/set_mode\n/mavros/cmd/arming\n/mavros/cmd/takeoff\n/mavros/cmd/land'),
            COMMANDS['fc_state']: (0, 'connected: true\narmed: false\n')}
        self.outputs.update({COMMANDS[name]: (0, expected)
                             for name, (_, _, expected) in EXPECTED_TYPES.items()})
        self.run = Mock(side_effect=lambda argv: self.outputs.get(tuple(argv), (0, '')))

    def checks(self, **kwargs):
        return diagnose('.', environ=kwargs.pop('environ', self.env), run=self.run,
                        disk_usage=lambda _: SimpleNamespace(free=4 * 1024**3),
                        devices=('/dev/ttyUSB0', '/dev/video0'), **kwargs)

    def test_all_checks_read_only_and_camera_opt_in(self):
        self.assertTrue(all(check['status'] == 'pass' for check in self.checks()))
        self.assertEqual(self.run.call_count, len(COMMANDS))
        self.assertEqual({call.args[0] for call in self.run.call_args_list}, set(COMMANDS.values()))

    def test_unsourced_ros_skips_probes_and_no_environment_dump(self):
        checks = self.checks(environ={'TOKEN': 'private-sentinel'})
        self.assertEqual(self.run.call_count, 1)
        self.assertNotIn('private-sentinel', str(checks))
        self.assertIn('fail', [check['status'] for check in checks])

    def test_armed_or_disconnected_state_fails(self):
        for output in ('connected: true\narmed: true', 'connected: false\narmed: false', ''):
            self.outputs[COMMANDS['fc_state']] = (0, output)
            check = next(item for item in self.checks() if item['name'] == 'fc_state')
            self.assertEqual(check['status'], 'fail')

    def test_camera_probe_and_native_timeout(self):
        checks = self.checks(probe_camera=True)
        self.assertEqual(self.run.call_count, len(COMMANDS) + 1)
        self.assertEqual(checks[-1]['name'], 'camera_capture')
        with patch('drone_bringup.doctor.run_probe', return_value=(2, '')):
            self.assertEqual(bounded_run(('probe',)), (2, ''))

    def test_each_wrong_interface_type_fails(self):
        for name in EXPECTED_TYPES:
            original = self.outputs[COMMANDS[name]]
            self.outputs[COMMANDS[name]] = (0, 'std_msgs/msg/Bool')
            check = next(item for item in self.checks() if item['name'] == name)
            self.assertEqual(check['status'], 'fail')
            self.outputs[COMMANDS[name]] = original
