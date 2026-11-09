import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.diagnostics import diagnose, COMPONENTS


class DiagnosticsTests(unittest.TestCase):
    def test_missing_and_boundary(self):
        self.assertFalse(diagnose({}, False, None)['healthy'])
        ages = dict.fromkeys(COMPONENTS, .1)
        self.assertTrue(diagnose(ages, True, False)['healthy'])
        for bad in (1., -1, float('nan'), True):
            ages['camera'] = bad
            self.assertFalse(diagnose(ages, True, False)['healthy'])
