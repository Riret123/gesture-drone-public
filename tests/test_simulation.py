import unittest
from gesture_control.simulation import batch, trial


class SimulationTests(unittest.TestCase):
    def test_reproducibility_and_timeout(self):
        self.assertEqual(batch(5, 4), batch(5, 4))
        self.assertFalse(trial(0, steps=0))
        self.assertEqual(batch(5)['successes'], 5)
        with self.assertRaises(ValueError):
            batch(0)
