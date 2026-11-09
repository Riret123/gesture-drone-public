import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch


class LiveScriptGuardTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'test_flight_cmd_bridge.py'
        spec = importlib.util.spec_from_file_location('live_script_test', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_no_flags_refuses_before_ros_import(self):
        with self.assertRaises(SystemExit) as error:
            self.module.main([])
        self.assertEqual(error.exception.code, 2)

    def test_malformed_ack_rejected(self):
        for value in ('junk', 'land:UNKNOWN:detail', 'wrong:OK:detail', None):
            with self.assertRaises(ValueError):
                self.module.parse_ack(value)
        self.assertEqual(self.module.parse_ack('land:FAIL:service:timeout'),
                         ('land', 'FAIL', 'service:timeout'))

    def test_ack_matching_ignores_other_command(self):
        tester = self.module.BridgeTester.__new__(self.module.BridgeTester)
        tester._acks = []
        from unittest.mock import Mock
        from types import SimpleNamespace
        tester.pub = Mock()
        tester.node = Mock()
        clock = iter((0., .1, .2, .3))
        def spin(*args, **kwargs):
            if not tester._acks:
                tester._acks.append('land:OK:land=OK')
            else:
                tester._acks.append('open_palm:OK:takeoff=OK')
        with patch.object(self.module, 'rclpy', SimpleNamespace(spin_once=spin), create=True), \
                patch.object(self.module, 'String', SimpleNamespace, create=True), \
                patch.object(self.module.time, 'monotonic', side_effect=lambda: next(clock)):
            ack = tester.publish_and_wait_ack('open_palm')
        self.assertEqual(ack, 'open_palm:OK:takeoff=OK')
