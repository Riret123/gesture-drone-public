"""Every primitive x mode x connectivity x arming x landing-latch cell."""
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import test_bridge_adapter as fixture
from drone_bringup.flight_logic import FlightController


MODES = ('GUIDED', 'STABILIZE', 'LOITER', 'LAND', 'RTL', '')
OPERATIONS = (('set_mode', 'GUIDED'), ('set_mode', 'LOITER'),
              ('arm', True), ('takeoff', 2.), ('land', None))


def primitive_case(mode, connected, armed, latched, operation, value):
    def test(self):
        module = fixture.load_adapter()
        bridge = module.FlightCmdBridge.__new__(module.FlightCmdBridge)
        bridge._stopping = threading.Event()
        bridge._service_wait = bridge._service_timeout = 5.
        state = SimpleNamespace(mode=mode, connected=connected, armed=armed)
        bridge._state_watchdog = Mock()
        bridge._state_watchdog.current.return_value = state
        bridge._logic = FlightController(bridge._call, lambda: state)
        if latched:
            bridge._logic.latch_landing()
        epoch = bridge._logic.takeoff_ticket()
        bridge._logic._context.epoch = epoch
        bridge._logic._context.hold_epoch = epoch
        client = Mock()
        client.wait_for_service.return_value = True
        future = client.call_async.return_value
        future.done.return_value = True
        future.exception.return_value = None
        future.result.return_value = SimpleNamespace(success=True, mode_sent=True)
        bridge._clients = {operation: client}
        if operation == 'land':
            expected = True  # best effort even without connected observation
        elif operation == 'set_mode' and value == 'LOITER':
            expected = not latched
        elif operation == 'set_mode':
            expected = connected and not latched
        elif operation == 'arm':
            expected = connected and not latched and mode == 'GUIDED'
        else:
            expected = connected and not latched and mode == 'GUIDED' and armed
        self.assertEqual(bridge._call(operation, value), expected)
        self.assertEqual(client.call_async.call_count, int(expected))
    return test


class BridgePrimitiveMatrixTests(unittest.TestCase):
    pass


for _mode_index, _mode in enumerate(MODES):
    for _connected in (False, True):
        for _armed in (False, True):
            for _latched in (False, True):
                for _operation_index, (_operation, _value) in enumerate(OPERATIONS):
                    _name = f'test_m{_mode_index}_connected{_connected}_armed{_armed}_latch{_latched}_op{_operation_index}'
                    setattr(BridgePrimitiveMatrixTests, _name,
                            primitive_case(_mode, _connected, _armed, _latched, _operation, _value))
