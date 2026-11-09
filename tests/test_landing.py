import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.landing import LandingController


class LandingTests(unittest.TestCase):
    def test_phases_and_latch(self):
        c = LandingController()
        self.assertEqual(c.update(None).state, 'search')
        self.assertEqual(c.update((1, 0, 2)).state, 'align')
        self.assertEqual(c.update((0, 0, 2)).state, 'descend')
        self.assertEqual(c.update((0, 0, .2)).state, 'final')
        self.assertEqual(c.update((0, 0, .1), True).state, 'touchdown')
        self.assertEqual(c.update((1, 1, 2)).descent, 0)

    def test_faults_and_vector_limit(self):
        c = LandingController()
        out = c.update((10, 10, 2))
        self.assertLessEqual((out.vx ** 2 + out.vy ** 2) ** .5, .200001)
        self.assertEqual(c.update(None).state, 'abort')
        for pose in ((0, 0, -1), (float('nan'), 0, 1)):
            self.assertEqual(LandingController().update(pose).state, 'abort')
        self.assertEqual(LandingController().update((0, 0, 2), True).state, 'abort')
