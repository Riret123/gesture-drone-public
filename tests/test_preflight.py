import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.preflight import report, REQUIRED


class PreflightTests(unittest.TestCase):
    def test_strict_checks(self):
        self.assertEqual(report({})['result'], 'FAIL')
        inputs = dict.fromkeys(REQUIRED, True)
        self.assertEqual(report(inputs)['result'], 'PASS')
        for bad in ('true', 1, None, False):
            inputs['simulation'] = bad
            self.assertEqual(report(inputs)['result'], 'FAIL')
