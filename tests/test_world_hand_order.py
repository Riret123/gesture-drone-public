"""Aggregate gesture policy must not depend on image/world output ordering."""
from itertools import permutations
from types import SimpleNamespace
import unittest
from gesture_control.frame_classifier import classify_frame
from gesture_control.pose_features import PoseProfile
from gesture_control.safety import GestureSafety
from test_pose_features import pose


class WorldHandOrderTests(unittest.TestCase):
    def test_all_two_hand_label_permutations_have_same_aggregate_command(self):
        for labels, expected in (((True, True), 'open_palm'),
                                 ((False, False), 'emergency'),
                                 ((True, False), None)):
            world = [pose(opened) for opened in labels]
            image = [[SimpleNamespace(x=x, y=y) for x, y, z in points] for points in world]
            for image_order in permutations(image):
                for world_order in permutations(world):
                    gestures = classify_frame(list(image_order), world_hands=list(world_order),
                                              profile=PoseProfile())
                    policy = GestureSafety(frames=1, now=0.)
                    self.assertEqual(policy.update(gestures, .1), expected)

    def test_count_disagreement_cannot_renew_valid_input(self):
        image = [[SimpleNamespace(x=x, y=y) for x, y, z in pose(True)]]
        for worlds in ([], [pose(True), pose(True)]):
            gestures = classify_frame(image, world_hands=worlds, profile=PoseProfile())
            policy = GestureSafety(frames=1, now=0.)
            self.assertEqual(policy.update(gestures, 5.), 'land')
