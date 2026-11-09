"""Exercise actual adapter construction, not only __new__ fixtures."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from test_bridge_adapter import load_adapter


class InertNode:
    def __init__(self, name):
        self.clients = []

    def declare_parameter(self, name, default):
        return SimpleNamespace(value=default)

    def create_subscription(self, *args):
        return Mock()

    def create_publisher(self, *args):
        return Mock()

    def create_client(self, *args):
        client = Mock()
        self.clients.append(client)
        return client

    def create_timer(self, *args):
        return Mock()

    def destroy_node(self):
        return True


class StartupInhibitionTests(unittest.TestCase):
    def test_every_new_bridge_requires_observed_dwell_and_operator_reset(self):
        for _ in range(2):
            module = load_adapter(InertNode)
            now = [0.]
            with patch.object(module.time, 'monotonic', side_effect=lambda: now[0]):
                bridge = module.FlightCmdBridge()
            bridge._on_state(SimpleNamespace(connected=True, armed=False, mode='STABILIZE'))
            self.assertFalse(bridge._logic.handle('open_palm')[0])
            bridge._handle('operator_reset')
            self.assertIn(':FAIL:', bridge._ack_pub.publish.call_args.args[0].data)
            for tick in range(6):
                now[0] = float(tick)
                bridge._on_state(SimpleNamespace(connected=True, armed=False, mode='STABILIZE'))
                bridge._logic.observe_reset_state()
            bridge._handle('operator_reset')
            self.assertIn(':OK:', bridge._ack_pub.publish.call_args.args[0].data)
            for client in bridge.clients:
                client.call_async.assert_not_called()
            bridge.destroy_node()
