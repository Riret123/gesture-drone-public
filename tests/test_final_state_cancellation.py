from types import SimpleNamespace
import unittest
from unittest.mock import Mock
import test_bridge_adapter as fixture
from drone_bringup.flight_logic import FlightController


class FinalStateCancellationTests(unittest.TestCase):
    def test_safety_arriving_during_controller_state_read_blocks_guided(self):
        state = SimpleNamespace(connected=True, armed=False)
        calls, reads = [], [0]
        def read():
            reads[0] += 1
            if reads[0] == 2:
                logic.handle('emergency')
            return state
        logic = FlightController(lambda op, value: calls.append((op, value)) or True, read)
        self.assertFalse(logic.handle('open_palm')[0])
        self.assertNotIn(('set_mode', 'GUIDED'), calls)
        self.assertNotIn(('arm', True), calls)

    def test_permission_rechecks_epoch_after_state_getter(self):
        state = SimpleNamespace(connected=True, armed=False)
        def read():
            logic.latch_landing()
            return state
        logic = FlightController(Mock(return_value=True), read)
        logic._context.epoch = logic.takeoff_ticket()
        self.assertFalse(logic.takeoff_permitted())

    def test_adapter_state_read_landing_prevents_arm_submission(self):
        fixture_case = fixture.BridgeAdapterTests()
        fixture_case.setUp()
        bridge = fixture_case.bridge
        state = SimpleNamespace(connected=True, armed=True, mode='GUIDED')
        logic = FlightController(Mock(return_value=True), lambda: state)
        logic._context.epoch = logic.takeoff_ticket()
        bridge._logic = logic
        def read():
            logic.handle('land')
            return state
        bridge._state_watchdog.current.side_effect = read
        self.assertFalse(bridge._call('arm', True))
        fixture_case.client.call_async.assert_not_called()
