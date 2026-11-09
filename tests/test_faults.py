import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.faults import campaign


class FaultTests(unittest.TestCase):
    def test_fault_campaign(self):
        outcomes = campaign()
        self.assertEqual(len(outcomes), 5)
        self.assertTrue(all(outcomes.values()), outcomes)
