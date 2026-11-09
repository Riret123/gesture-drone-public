"""Actual bridge watchdog and reception paths, inert ROS doubles only."""
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_bridge_adapter import load_adapter
from drone_bringup.flight_logic import FlightController
from drone_bringup.service_circuit import ServiceCircuit


class BridgeLinkGuardTests(unittest.TestCase):
    def setUp(self):
        self.module = load_adapter()
        self.bridge = self.module.FlightCmdBridge.__new__(self.module.FlightCmdBridge)
        self.bridge._stopping = threading.Event()
        self.bridge._state_watchdog = Mock()
        self.bridge._state_watchdog.current.return_value = SimpleNamespace(
            connected=True, armed=False)
        self.bridge._logic = Mock()
        self.bridge._link_was_connected = self.bridge._link_loss_sent = False

    def test_no_startup_land_then_one_loss_attempt(self):
        bridge = self.bridge
        bridge._on_flight_cmd = Mock()
        bridge._state_watchdog.current.return_value = None
        bridge._check_link()
        bridge._on_flight_cmd.assert_not_called()
        bridge._state_watchdog.current.return_value = SimpleNamespace(connected=True)
        bridge._check_link()
        bridge._state_watchdog.current.return_value = None
        for _ in range(100):
            bridge._check_link()
        bridge._on_flight_cmd.assert_called_once()
        self.assertEqual(bridge._on_flight_cmd.call_args.args[0].data, 'emergency')

    def test_shutdown_stops_watchdog(self):
        self.bridge._stopping.set()
        self.bridge._check_link()
        self.bridge._logic.observe_reset_state.assert_not_called()

    def test_busy_landing_still_latches_and_blocks_takeoff(self):
        bridge = self.bridge
        bridge._logic = FlightController(Mock(return_value=True),
                                         bridge._state_watchdog.current)
        bridge._admission = Mock()
        bridge._admission.acquire.return_value = None
        bridge._ack_pub = Mock()
        bridge._on_flight_cmd(SimpleNamespace(data='land'))
        self.assertFalse(bridge._logic.handle('open_palm')[0])
        self.assertIn('busy', bridge._ack_pub.publish.call_args.args[0].data)

    def test_circuit_wraps_actual_service_timeout_without_retry(self):
        bridge = self.bridge
        bridge._circuit = ServiceCircuit()
        bridge._call_once = Mock(return_value=False)
        for _ in range(100):
            self.assertFalse(bridge._call('arm', True))
        self.assertEqual(bridge._call_once.call_count, 3)
        bridge._call_once.return_value = True
        self.assertTrue(bridge._call('land', None))

    def test_land_reception_latches_before_thread_creation(self):
        bridge = self.bridge
        bridge._logic = FlightController(Mock(return_value=True),
                                         bridge._state_watchdog.current)
        bridge._admission = Mock()
        with patch.object(self.module.threading, 'Thread', side_effect=RuntimeError('thread')):
            with self.assertRaises(RuntimeError):
                bridge._on_flight_cmd(SimpleNamespace(data='emergency'))
        self.assertFalse(bridge._logic.handle('open_palm')[0])
        bridge._admission.release.assert_called_once()
