"""Synthetic orientation invariance; these fixtures do not measure accuracy."""
import math
import unittest
from gesture_control.pose_features import PoseProfile, classify_pose, calibrate


def pose(extended):
    points = [(0., 0., 0.)] * 21
    for finger, base in enumerate((5, 9, 13, 17)):
        x = float(finger + 1)
        points[base] = (x, 1., 0.)
        points[base + 1] = (x, 2., 0.)
        points[base + 2] = (x, 3., 0.) if extended else (x, 2., 1.)
        points[base + 3] = (x, 4., 0.) if extended else (x, 1., 1.)
    return points


class PoseFeaturesTests(unittest.TestCase):
    def test_front_back_and_rotation_invariance(self):
        for opened, expected in ((True, 'open_palm'), (False, 'fist')):
            for angle in (0, .4, math.pi, -1.2):
                c, s = math.cos(angle), math.sin(angle)
                points = [(c*x + s*z + 7, y - 4, -s*x + c*z)
                          for x, y, z in pose(opened)]
                result = classify_pose(points, PoseProfile())
                self.assertEqual(result.gesture, expected)
                self.assertGreaterEqual(result.confidence, .5)

    def test_invalid_and_collapsed_geometry(self):
        for value in (None, [], [(0., 0., 0.)] * 21,
                      [(float('nan'), 0., 0.)] * 21):
            self.assertEqual(classify_pose(value, PoseProfile()).gesture, 'other')

    def test_ambiguous_finger_is_not_takeoff(self):
        points = pose(True)
        points[7] = (1., 2., 1.)
        points[8] = (1., 1., 1.)
        self.assertEqual(classify_pose(points, PoseProfile()).gesture, 'other')

    def test_calibration_requires_separation_and_sample_count(self):
        with self.assertRaises(ValueError):
            calibrate([pose(True)], [pose(False)])
        with self.assertRaises(ValueError):
            calibrate([pose(True)] * 5, [pose(True)] * 5)
        profile = calibrate([pose(True)] * 5, [pose(False)] * 5)
        self.assertEqual(classify_pose(pose(True), profile).gesture, 'open_palm')
        self.assertEqual(classify_pose(pose(False), profile).gesture, 'fist')

    def test_invalid_profile(self):
        for kwargs in ({'folded_max': True}, {'extended_min': 80},
                       {'min_confidence': float('nan')}, {'min_confidence': 1.1}):
            with self.assertRaises(ValueError):
                PoseProfile(**kwargs)
