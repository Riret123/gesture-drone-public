"""State age is measured on the companion's monotonic receive clock."""
import unittest
from types import SimpleNamespace
from drone_bringup.state_watchdog import StateWatchdog


class StateWatchdogTests(unittest.TestCase):
    def test_boundary_and_snapshot(self):
        clock = [10.0]
        guard = StateWatchdog(lambda: clock[0], 2.0)
        self.assertIsNone(guard.current())
        msg = SimpleNamespace(connected=True, armed=False, mode='GUIDED')
        guard.receive(msg)
        msg.armed = True
        self.assertFalse(guard.current().armed)
        clock[0] = 11.999
        self.assertIsNotNone(guard.current())
        clock[0] = 12.0
        self.assertIsNone(guard.current())

    def test_invalid_clock_revokes_state(self):
        for invalid in (float('nan'), float('inf'), True, '12', 9.0):
            clock = [10.0]
            guard = StateWatchdog(lambda: clock[0])
            guard.receive(SimpleNamespace(connected=True, armed=False))
            clock[0] = invalid
            self.assertIsNone(guard.current())
            clock[0] = 10.0
            self.assertIsNone(guard.current())

    def test_bad_message_revokes_state(self):
        guard = StateWatchdog(lambda: 1.0)
        for value in (None, SimpleNamespace(connected=1, armed=False),
                      SimpleNamespace(connected=True, armed='no')):
            guard.receive(SimpleNamespace(connected=True, armed=False))
            guard.receive(value)
            self.assertIsNone(guard.current())

    def test_config(self):
        for value in (0, -1, True, float('nan'), '2'):
            with self.assertRaises(ValueError):
                StateWatchdog(lambda: 0.0, value)
