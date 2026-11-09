"""Execute the actual ROS adapter against inert request/client doubles."""
import importlib.util
from pathlib import Path
import sys
import threading
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import Mock, patch


def load_adapter(node_class=None):
    modules = {name: ModuleType(name) for name in (
        'rclpy', 'rclpy.node', 'mavros_msgs', 'mavros_msgs.msg',
        'mavros_msgs.srv', 'std_msgs', 'std_msgs.msg')}
    modules['rclpy.node'].Node = node_class if node_class is not None else object
    modules['mavros_msgs.msg'].State = SimpleNamespace
    for name in ('CommandBool', 'CommandTOL', 'SetMode'):
        setattr(modules['mavros_msgs.srv'], name,
                SimpleNamespace(Request=lambda **kwargs: SimpleNamespace(**kwargs)))
    modules['std_msgs.msg'].String = lambda **kwargs: SimpleNamespace(**kwargs)
    path = Path(__file__).resolve().parents[1] / (
        'src/drone_bringup/drone_bringup/flight_cmd_bridge.py')
    spec = importlib.util.spec_from_file_location('bridge_test_adapter', path)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, modules):
        spec.loader.exec_module(module)
    return module


class BridgeAdapterTests(unittest.TestCase):
    def setUp(self):
        self.module = load_adapter()
        self.bridge = self.module.FlightCmdBridge.__new__(self.module.FlightCmdBridge)
        self.bridge._service_wait = self.bridge._service_timeout = 5.0
        self.bridge._stopping = threading.Event()
        self.bridge._transition_timeout = 5.0
        self.bridge._state_watchdog = Mock()
        self.bridge._state_watchdog.current.return_value = SimpleNamespace(
            connected=True, armed=True, mode='GUIDED')
        self.bridge._logic = Mock()
        self.bridge._logic.takeoff_permitted.return_value = True
        self.bridge._logic.hold_permitted.return_value = True
        self.client = Mock()
        self.client.wait_for_service.return_value = True
        self.future = self.client.call_async.return_value
        self.future.done.return_value = True
        self.future.exception.return_value = None
        self.future.result.return_value = SimpleNamespace(success=True, mode_sent=True)
        self.bridge._clients = dict.fromkeys(('set_mode', 'arm', 'takeoff', 'land'),
                                             self.client)

    def test_request_fields_and_acceptance(self):
        for operation, value, field in (('set_mode', 'GUIDED', 'custom_mode'),
                                         ('arm', True, 'value'),
                                         ('takeoff', 2.0, 'altitude')):
            with self.subTest(operation=operation):
                self.assertTrue(self.bridge._call(operation, value))
                request = self.client.call_async.call_args.args[0]
                self.assertEqual(getattr(request, field), value)
        self.assertTrue(self.bridge._call('land', None))

    def test_missing_service_sends_nothing(self):
        self.client.wait_for_service.return_value = False
        self.assertFalse(self.bridge._call('arm', True))
        self.client.call_async.assert_not_called()

    def test_response_failure_and_exception(self):
        for response in (None, SimpleNamespace(success=False)):
            self.future.result.return_value = response
            self.assertFalse(self.bridge._call('land', None))
        self.future.exception.return_value = RuntimeError('service failed')
        self.assertFalse(self.bridge._call('land', None))

    def test_response_timeout_is_failure(self):
        self.future.done.return_value = False
        with patch.object(self.module.time, 'monotonic', side_effect=[0, 6]):
            self.assertFalse(self.bridge._call('arm', True))

    def test_ack_exception_is_fail(self):
        self.bridge._logic = Mock()
        self.bridge._logic.handle.side_effect = RuntimeError('test error')
        self.bridge._ack_pub = Mock()
        self.bridge._handle('open_palm')
        self.assertEqual(self.bridge._ack_pub.publish.call_args.args[0].data,
                         'open_palm:FAIL:test error')

    def test_safety_revocation_while_waiting_prevents_arm_send(self):
        def available(**kwargs):
            self.bridge._logic.takeoff_permitted.return_value = False
            return True
        self.client.wait_for_service.side_effect = available
        self.assertFalse(self.bridge._call('arm', True))
        self.client.call_async.assert_not_called()

    def test_safety_revocation_does_not_block_landing(self):
        self.bridge._logic.takeoff_permitted.return_value = False
        self.assertTrue(self.bridge._call('land', None))

    def test_shutdown_during_service_wait_prevents_submission(self):
        def available(**kwargs):
            self.bridge._stopping.set()
            return True
        self.client.wait_for_service.side_effect = available
        self.assertFalse(self.bridge._call('land', None))
        self.client.call_async.assert_not_called()

    def test_shutdown_does_not_publish_late_ack(self):
        self.bridge._stopping.set()
        self.bridge._logic.handle.return_value = (True, 'test')
        self.bridge._ack_pub = Mock()
        self.bridge._handle('land')
        self.bridge._ack_pub.publish.assert_not_called()

    def test_transition_confirmation_requires_mode_and_armed_observation(self):
        self.bridge._state_watchdog.current.return_value = SimpleNamespace(
            connected=True, armed=True, mode='GUIDED')
        self.assertTrue(self.bridge._confirm('set_mode', 'GUIDED'))
        self.assertTrue(self.bridge._confirm('arm', True))

    def test_transition_timeout_or_safety_revocation(self):
        self.bridge._state_watchdog.current.return_value = SimpleNamespace(
            connected=True, armed=False, mode='STABILIZE')
        with patch.object(self.module.time, 'monotonic', side_effect=[0., 6.]):
            self.assertFalse(self.bridge._confirm('set_mode', 'GUIDED'))
        self.bridge._logic.takeoff_permitted.return_value = False
        self.assertFalse(self.bridge._confirm('arm', True))

    def test_delayed_transition_is_observed_not_assumed(self):
        self.bridge._state_watchdog.current.side_effect = [
            SimpleNamespace(connected=True, armed=False, mode='STABILIZE'),
            SimpleNamespace(connected=True, armed=False, mode='GUIDED')]
        with patch.object(self.module.time, 'monotonic', side_effect=[0., .1, .2]), \
                patch.object(self.module.time, 'sleep') as pause:
            self.assertTrue(self.bridge._confirm('set_mode', 'GUIDED'))
        pause.assert_called_once_with(.02)

    def test_pilot_mode_change_prevents_arm_and_takeoff(self):
        self.bridge._state_watchdog.current.return_value = SimpleNamespace(
            connected=True, armed=True, mode='LAND')
        for operation, value in (('arm', True), ('takeoff', 2.0)):
            self.assertFalse(self.bridge._call(operation, value))
        self.client.call_async.assert_not_called()

    def test_disarmed_state_prevents_takeoff_request(self):
        self.bridge._state_watchdog.current.return_value = SimpleNamespace(
            connected=True, armed=False, mode='GUIDED')
        self.assertFalse(self.bridge._call('takeoff', 2.0))
        self.client.call_async.assert_not_called()

    def test_landing_during_hold_service_wait_prevents_loiter_send(self):
        def available(**kwargs):
            self.bridge._logic.hold_permitted.return_value = False
            return True
        self.client.wait_for_service.side_effect = available
        self.assertFalse(self.bridge._call('set_mode', 'LOITER'))
        self.client.call_async.assert_not_called()
