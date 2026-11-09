import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.geofence import evaluate


class GeofenceTests(unittest.TestCase):
    def test_boundaries(self):
        self.assertEqual(evaluate(0, 0, 2, 90), 'allow')
        for args in ((20, 0, 2, 90), (0, 0, 5, 90), (0, 0, 2, 25)):
            self.assertEqual(evaluate(*args), 'rtl')
        self.assertEqual(evaluate(float('nan'), 0, 2, 50), 'hold')
        with self.assertRaises(ValueError):
            evaluate(0, 0, 1, 50, radius=-1)
