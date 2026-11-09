from types import SimpleNamespace
import unittest
from unittest.mock import Mock
from gesture_control.world_capture import collect_world
from test_pose_features import pose


class WorldCaptureTests(unittest.TestCase):
    def setUp(self):
        self.now = 0.
        self.cap, self.hands = Mock(), Mock()
        self.cap.read.return_value = (True, object())
        self.number = 0
        def process(image):
            self.now += .03
            self.number += 1
            points = [SimpleNamespace(x=x+self.number*.001, y=y, z=z) for x, y, z in pose(True)]
            return SimpleNamespace(multi_hand_world_landmarks=[SimpleNamespace(landmark=points)],
                                   multi_hand_landmarks=[object()])
        self.hands.process.side_effect = process

    def collect(self, **kwargs):
        return collect_world(self.cap, self.hands, lambda image: image,
                             lambda: self.now, target=5, **kwargs)

    def test_distinct_one_hand_world_frames_and_completion_clock(self):
        frames, report = self.collect()
        self.assertTrue(report['complete'])
        self.assertEqual(len(frames), 5)
        self.assertTrue(all(b.time > a.time for a, b in zip(frames, frames[1:])))

    def test_frozen_or_missing_world_is_bounded_and_incomplete(self):
        points = [SimpleNamespace(x=x, y=y, z=z) for x, y, z in pose(True)]
        self.hands.process.side_effect = None
        self.hands.process.return_value = SimpleNamespace(
            multi_hand_world_landmarks=[SimpleNamespace(landmark=points)], multi_hand_landmarks=[object()])
        frames, report = self.collect()
        self.assertFalse(report['complete'])
        self.assertLessEqual(len(frames), 1)
        self.assertEqual(report['attempts'], 100)

    def test_slow_samples_and_deadline_do_not_get_saved(self):
        original = self.hands.process.side_effect
        def slow(image):
            result = original(image)
            self.now += .3
            return result
        self.hands.process.side_effect = slow
        frames, report = self.collect(timeout=1.)
        self.assertEqual(frames, ())
        self.assertFalse(report['complete'])

    def test_clock_reverse_rejects(self):
        with self.assertRaises(ValueError):
            collect_world(self.cap, self.hands, lambda image: image,
                          iter((1., 0.)).__next__, target=5)
