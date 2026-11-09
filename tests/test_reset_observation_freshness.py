from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from drone_bringup.flight_logic import FlightController
from drone_bringup.state_watchdog import StateWatchdog


class ResetObservationFreshnessTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.
        self.watchdog = StateWatchdog(lambda: self.now, max_age=10.)
        self.logic = FlightController(Mock(return_value=True), self.watchdog.current,
                                      clock=lambda: self.now, startup_latched=True)
        self.sample = SimpleNamespace(connected=True, armed=False, mode='STABILIZE')

    def test_cached_disarm_cannot_accumulate_dwell(self):
        self.watchdog.receive(self.sample)
        for index in range(61):
            self.now = index / 10
            self.logic.observe_reset_state()
        self.assertFalse(self.logic.operator_reset()[0])

    def test_distinct_fresh_samples_and_no_gap_allow_reset(self):
        for tick in range(6):
            self.now = float(tick)
            self.watchdog.receive(self.sample)
            self.logic.observe_reset_state()
        self.assertTrue(self.logic.operator_reset()[0])

    def test_pre_landing_disarm_sample_cannot_seed_new_dwell(self):
        self.watchdog.receive(self.sample)
        self.now = 1.
        self.logic.handle('land')
        self.assertFalse(self.logic.observe_reset_state())
        for tick in range(2, 7):
            self.now = float(tick)
            self.watchdog.receive(self.sample)
            self.logic.observe_reset_state()
        self.assertFalse(self.logic.operator_reset()[0])  # only four observed seconds
        self.now = 7.
        self.watchdog.receive(self.sample)
        self.assertTrue(self.logic.operator_reset()[0])
