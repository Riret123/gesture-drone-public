"""Regression counterexamples on the live pure-Python control path."""
import unittest
from types import SimpleNamespace
from gesture_control.gesture_classifier import classify_gesture
from drone_bringup.flight_logic import FlightController


class CoreRegressionTests(unittest.TestCase):
    def test_old_disarmed_snapshot_cannot_skip_land_during_pending_arm(self):
        calls = []
        state = SimpleNamespace(connected=True, armed=False)
        def service(name, value):
            calls.append((name, value))
            if name == 'arm':
                # FC arming response/state update has not reached the companion.
                controller.handle('emergency')
                state.armed = True
            return True
        controller = FlightController(service, lambda: state)
        self.assertFalse(controller.handle('open_palm')[0])
        self.assertIn(('land', None), calls)
        self.assertNotIn(('takeoff', 2.), calls)

    def test_unconfirmed_guided_prevents_arming(self):
        calls = []
        controller = FlightController(lambda *args: calls.append(args) or True,
            lambda: SimpleNamespace(connected=True, armed=False),
            confirm=lambda *args: False)
        self.assertFalse(controller.handle('open_palm')[0])
        self.assertEqual(calls, [('set_mode', 'GUIDED')])

    def test_unconfirmed_arm_prevents_takeoff(self):
        calls = []
        controller = FlightController(lambda *args: calls.append(args) or True,
            lambda: SimpleNamespace(connected=True, armed=False),
            confirm=lambda name, value: name == 'set_mode')
        self.assertFalse(controller.handle('open_palm')[0])
        self.assertEqual(calls, [('set_mode', 'GUIDED'), ('arm', True)])

    def test_older_hold_cannot_override_newer_landing(self):
        calls = []
        controller = FlightController(lambda *args: calls.append(args) or True,
            lambda: SimpleNamespace(connected=True, armed=True))
        ticket = controller.takeoff_ticket()
        controller.handle('land')
        self.assertFalse(controller.handle('hold', ticket=ticket)[0])
        self.assertEqual(calls, [('land', None)])

    def test_safety_invalidates_admitted_but_unscheduled_takeoff(self):
        calls = []
        controller = FlightController(lambda *args: calls.append(args) or True,
            lambda: SimpleNamespace(connected=True, armed=False))
        ticket = controller.takeoff_ticket()
        controller.handle('emergency')
        self.assertFalse(controller.handle('open_palm', ticket=ticket)[0])
        self.assertEqual(calls, [])

    def test_invalid_landmarks_never_become_flight_gestures(self):
        for value in (float('nan'), float('inf'), True, '0'):
            points = [SimpleNamespace(x=value, y=0.0) for _ in range(21)]
            with self.subTest(value=value):
                self.assertEqual(classify_gesture(points), 'other')

    def test_collapsed_hand_is_unknown(self):
        self.assertEqual(classify_gesture(
            [SimpleNamespace(x=0.0, y=0.0) for _ in range(21)]), 'other')

    def test_bad_shape_is_unknown(self):
        for points in (None, [], [None] * 21):
            self.assertEqual(classify_gesture(points), 'other')

    def test_disconnect_after_guided_prevents_arm(self):
        state = SimpleNamespace(connected=True, armed=False)
        calls = []
        def service(name, value):
            calls.append((name, value))
            state.connected = False
            return True
        controller = FlightController(service, lambda: state)
        self.assertFalse(controller.handle('open_palm')[0])
        self.assertEqual(calls, [('set_mode', 'GUIDED')])

    def test_disconnected_disarmed_state_does_not_skip_emergency(self):
        calls = []
        controller = FlightController(
            lambda *args: calls.append(args) or True,
            lambda: SimpleNamespace(connected=False, armed=False))
        controller.handle('emergency')
        self.assertEqual(calls, [('land', None)])

    def test_takeoff_rejected_during_landing_or_hold(self):
        for safety in ('land', 'hold'):
            calls = []
            nested = []
            def service(name, value):
                calls.append((name, value))
                if (name == 'land' or value == 'LOITER'):
                    nested.append(controller.handle('open_palm'))
                return True
            controller = FlightController(service, lambda: SimpleNamespace(
                connected=True, armed=True))
            controller.handle(safety)
            self.assertFalse(nested[0][0])
            self.assertNotIn(('takeoff', 2.0), calls)
