import importlib.util
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
import sys


class LegacySitlFailfastTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'test_flight_cmd_bridge.py'
        spec = importlib.util.spec_from_file_location('legacy_failfast_fixture', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.tester = Mock()
        self.tester.node.count_publishers.return_value = 1
        self.tester.wait_for_bridge_subscriber.return_value = True
        self.tester.wait_for_armed.return_value = True

    def test_uncertain_first_ack_never_causes_duplicate_takeoff(self):
        for ack in (None, 'open_palm:FAIL:set_mode=FAIL', 'land:OK:wrong command'):
            self.tester.publish_and_wait_ack.reset_mock()
            self.tester.publish_and_wait_ack.return_value = ack
            with self.assertRaises(RuntimeError):
                self.module.run_legacy_checks(self.tester)
            self.tester.publish_and_wait_ack.assert_called_once_with('open_palm')

    def test_legacy_sequence_checks_landing_inhibition(self):
        self.tester.publish_and_wait_ack.side_effect = (
            'open_palm:OK:takeoff(2.0m)=OK', 'open_palm:OK:arm=SKIP(already armed)',
            'fist:OK:land=OK', 'fist:OK:land=SKIP(disarmed)',
            'open_palm:FAIL:takeoff blocked by landing latch; operator reset required',
            'other:OK:no action')
        self.assertTrue(self.module.run_legacy_checks(self.tester))
        self.assertEqual([call.args[0] for call in self.tester.publish_and_wait_ack.call_args_list],
                         ['open_palm', 'open_palm', 'fist', 'fist', 'open_palm', 'other'])

    def test_failure_still_cleans_up_ros_and_node(self):
        ros = Mock()
        modules = {'rclpy': ros, 'mavros_msgs.msg': SimpleNamespace(State=object),
                   'std_msgs.msg': SimpleNamespace(String=object)}
        with patch.dict(sys.modules, modules), \
                patch.object(self.module, 'BridgeTester', return_value=self.tester), \
                patch.object(self.module, 'run_legacy_checks', side_effect=RuntimeError('synthetic')), \
                patch('builtins.print'):
            self.assertEqual(self.module.main(['--sitl-isolated', '--fcu-url', 'udp://:14550@']), 1)
        self.tester.shutdown.assert_called_once()
        ros.shutdown.assert_called_once()
