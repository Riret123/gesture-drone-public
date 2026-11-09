"""Full camera-independent chain through mocked MAVROS and FC state."""
import unittest
from types import SimpleNamespace
from gesture_control.gesture_classifier import classify_gesture, FINGER_TIP_MCP
from gesture_control.safety import GestureSafety
from drone_bringup.flight_logic import FlightController
from drone_bringup.state_watchdog import StateWatchdog


def hand(open_hand):
    points = [SimpleNamespace(x=0.0, y=0.0) for _ in range(21)]
    for tip, base in FINGER_TIP_MCP:
        points[base] = SimpleNamespace(x=1.0, y=0.0)
        points[tip] = SimpleNamespace(x=3.0 if open_hand else 0.8, y=0.0)
    return points


class ChainTests(unittest.TestCase):
    def setUp(self):
        self.clock = [0.0]
        self.state = SimpleNamespace(connected=True, armed=False)
        self.watchdog = StateWatchdog(lambda: self.clock[0])
        self.watchdog.receive(self.state)
        self.calls = []
        self.policy = GestureSafety(frames=2)
        self.controller = FlightController(self.service, self.watchdog.current)

    def service(self, operation, value):
        self.calls.append((operation, value))
        if operation == 'arm':
            self.state.armed = value
            self.watchdog.receive(self.state)
        return True

    def frame(self, hands, now):
        self.clock[0] = now
        command = self.policy.update([classify_gesture(p) for p in hands], now)
        return self.controller.handle(command) if command else None

    def test_takeoff_loss_hold_land(self):
        self.assertIsNone(self.frame([hand(True)], .1))
        self.assertTrue(self.frame([hand(True)], .2)[0])
        self.assertEqual(self.calls, [('set_mode', 'GUIDED'), ('arm', True),
                                      ('takeoff', 2.0)])
        self.assertTrue(self.frame([], 2.2)[0])
        self.assertEqual(self.calls[-1], ('set_mode', 'LOITER'))
        self.assertTrue(self.frame([], 5.2)[0])
        self.assertEqual(self.calls[-1], ('land', None))

    def test_stale_fc_state_blocks_takeoff(self):
        self.frame([hand(True)], 2.1)
        result = self.frame([hand(True)], 2.2)
        self.assertFalse(result[0])
        self.assertEqual(self.calls, [('set_mode', 'LOITER')])

    def test_two_fists_immediately_interrupt_debounce(self):
        self.frame([hand(True)], .1)
        self.state.armed = True
        self.watchdog.receive(self.state)
        self.assertTrue(self.frame([hand(False), hand(False)], .1)[0])
        self.assertEqual(self.calls, [('land', None)])

    def test_service_rejection_does_not_arm(self):
        self.controller.call = lambda *args: False
        self.frame([hand(True)], .1)
        self.assertFalse(self.frame([hand(True)], .2)[0])
        self.assertFalse(self.state.armed)
