import importlib.util
from pathlib import Path
import unittest
import sys
from types import SimpleNamespace
from unittest.mock import Mock, patch


class SitlRosRunnerTests(unittest.TestCase):
    def setUp(self):
        path = Path(__file__).resolve().parents[1] / 'tools/sitl_ros_scenarios.py'
        spec = importlib.util.spec_from_file_location('sitl_runner_test', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)

    def test_plan_imports_no_ros_and_never_executes(self):
        with patch.object(self.module, 'run_live') as live, patch('builtins.print'):
            self.assertEqual(self.module.main(['takeoff']), 0)
        live.assert_not_called()

    def test_execution_requires_all_isolation_flags(self):
        for args in (['takeoff', '--execute'],
                     ['takeoff', '--execute', '--sitl-isolated'],
                     ['takeoff', '--execute', '--sitl-isolated', '--fcu-url', '/dev/ttyUSB0:921600'],
                     ['rc-loss', '--execute', '--sitl-isolated', '--fcu-url', 'udp://:14550@']):
            with self.subTest(args=args), patch.object(self.module, 'run_live') as live:
                with self.assertRaises(SystemExit) as error:
                    self.module.main(args)
                self.assertEqual(error.exception.code, 2)
                live.assert_not_called()

    def test_fault_restore_attempted_after_uncertain_injection(self):
        transport = self.module.LiveTransport.__new__(self.module.LiveTransport)
        transport._fault_attempted = False
        transport._set_sim_rc = Mock(side_effect=[False, True])
        transport.observations = Mock()
        self.assertFalse(transport.fault('rc_loss'))
        self.assertTrue(transport.restore_fault())
        self.assertEqual([c.args[0] for c in transport._set_sim_rc.call_args_list], [1, 0])

    def test_no_unrelated_parameter_mutation(self):
        transport = self.module.LiveTransport.__new__(self.module.LiveTransport)
        transport._set_sim_rc = Mock()
        with self.assertRaises(ValueError):
            transport.fault('disable_failsafes')
        transport._set_sim_rc.assert_not_called()

    def test_scenario_exception_restores_fault_and_cleans_up(self):
        ros, transport = Mock(), Mock()
        transport.verify_simulator_parameter.return_value = True
        transport.restore_fault.return_value = True
        with patch.dict(sys.modules, {'rclpy': ros}), \
                patch.object(self.module, 'LiveTransport', return_value=transport), \
                patch.object(self.module, 'run_scenario', side_effect=RuntimeError('test fault')), \
                patch('builtins.print'):
            self.assertEqual(self.module.run_live(SimpleNamespace(rc_mode='LAND',
                                                                  scenario='takeoff')), 1)
        transport.restore_fault.assert_called_once()
        transport.node.destroy_node.assert_called_once()
        ros.shutdown.assert_called_once()

    def test_restore_exception_is_reported_as_failure(self):
        ros, transport = Mock(), Mock()
        transport.verify_simulator_parameter.return_value = True
        transport.restore_fault.side_effect = RuntimeError('link lost')
        with patch.dict(sys.modules, {'rclpy': ros}), \
                patch.object(self.module, 'LiveTransport', return_value=transport), \
                patch.object(self.module, 'run_scenario', return_value=(True, 'done')), \
                patch('builtins.print'):
            self.assertEqual(self.module.run_live(SimpleNamespace(rc_mode='LAND',
                                                                  scenario='rc-loss')), 1)
        transport.node.destroy_node.assert_called_once()
        ros.shutdown.assert_called_once()
