import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.extended_gestures import classify


def fixture(fingers, thumb_y=-1):
    p = [(.08, 0.)] * 21
    p[0] = (0., 0.)
    for i in (2, 5, 9, 13, 17):
        p[i] = (.1, 0.)
    for i in fingers:
        p[(4, 8, 12, 16, 20)[i]] = (0., thumb_y if i == 0 else -1.)
    return p


class ExtendedTests(unittest.TestCase):
    def test_fixtures(self):
        for fingers, expected in (([], 'fist'), ([0], 'thumbs_up'),
                                   ([1], 'pointing'), ([1, 2], 'peace'),
                                   ([0, 1, 2, 3, 4], 'open_palm')):
            self.assertEqual(classify(fixture(fingers)), expected)
        self.assertEqual(classify(fixture([0], 1)), 'thumbs_down')
        self.assertEqual(classify([]), 'other')
