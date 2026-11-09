"""Independent sampled-time reset model across FC stream rates and dwell bounds."""
from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from drone_bringup.flight_logic import FlightController
from drone_bringup.state_watchdog import StateWatchdog


class ResetDwellModelTests(unittest.TestCase):
    def test_stream_rate_and_dwell_product_matches_independent_model(self):
        for delay in (1., 5., 60.):
            for interval in (1, 5, 10, 19, 20, 21):  # units of 0.1 second
                with self.subTest(delay=delay, interval=interval):
                    clock = [0.]
                    guard = StateWatchdog(lambda: clock[0], max_age=10.)
                    service = Mock(return_value=True)
                    logic = FlightController(service, guard.current, clock=lambda: clock[0],
                                              reset_delay=delay, startup_latched=True)
                    state = SimpleNamespace(connected=True, armed=False)
                    first = last = None
                    for tick in range(651):
                        clock[0] = tick / 10.
                        if tick % interval == 0:
                            if last is None or tick-last >= 20:
                                first = tick
                            last = tick
                            guard.receive(state)
                        fresh = last is not None and tick-last < 20
                        if not fresh:
                            first = None
                        expected = fresh and first is not None and last-first >= delay*10
                        actual, _ = logic.operator_reset()
                        self.assertEqual(actual, expected, (delay, interval, tick))
                    service.assert_not_called()
