import unittest
from drone_bringup.flight_logic import FlightController
from gesture_control.gesture_classifier import classify_gesture


class LiveConfigurationTests(unittest.TestCase):
    def test_altitude_invalid_configuration(self):
        for value in (0, -1, True, '2', float('nan'), float('inf'), 10 ** 1000,
                      2.01, 1e300):
            with self.assertRaises(ValueError):
                FlightController(lambda *args: True, lambda: None,
                                 takeoff_altitude=value)

    def test_ratio_invalid_configuration(self):
        for value in (0, -1, True, '1', float('nan'), float('inf'), 10 ** 1000,
                      1., 3.01, 1e300):
            with self.assertRaises(ValueError):
                classify_gesture([], curl_ratio=value)
