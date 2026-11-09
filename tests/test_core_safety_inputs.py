"""Hostile input and sampling interruptions must not confirm takeoff."""
import unittest
from gesture_control.safety import GestureSafety


class CoreSafetyInputs(unittest.TestCase):
    def test_boolean_and_malformed_times_reject_consistently(self):
        for value in (True, None, '2', 10 ** 1000):
            for field in ('hold_after', 'land_after', 'now'):
                with self.subTest(field=field, value=type(value).__name__):
                    with self.assertRaises(ValueError):
                        GestureSafety(**{field: value})
            with self.assertRaises(ValueError):
                GestureSafety().update([], value)

    def test_repeated_timestamp_does_not_confirm(self):
        safety = GestureSafety(frames=2)
        self.assertIsNone(safety.update(['open_palm'], 1.0))
        self.assertIsNone(safety.update(['open_palm'], 1.0))

    def test_sampling_gap_resets_confirmation(self):
        safety = GestureSafety(frames=2)
        safety.update(['open_palm'], 0.1)
        self.assertEqual(safety.update(['open_palm'], 3.0), 'hold')
        self.assertEqual(safety.update(['open_palm'], 3.1), 'open_palm')

    def test_bad_gesture_container_is_missing_input(self):
        for value in (None, 'fist', 3, [None], [['fist']]):
            safety = GestureSafety(frames=1)
            self.assertEqual(safety.update(value, 2.0), 'hold')
