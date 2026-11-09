"""Semantic identity and explicit coordinate-context refusal checks."""
from dataclasses import FrozenInstanceError
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.mission_binding import (BoundMission, MissionContext, bind,
                                             require_context, semantic_id)
from gesture_control.mission_schema import Mission, Waypoint


def mission(**kwargs):
    return Mission((Waypoint('a', 0, 0, 1),), **kwargs)


class MissionBindingTests(unittest.TestCase):
    def test_equal_numeric_representations_same_identifier(self):
        integer = Mission((Waypoint('a', 0, 0, 1, 0),), speed=1, radius=20, ceiling=5)
        decimal = Mission((Waypoint('a', -0.0, 0.0, 1.0, -0.0),), speed=1.0, radius=20.0, ceiling=5.0)
        self.assertEqual(integer, decimal)
        self.assertEqual(semantic_id(integer), semantic_id(decimal))

    def test_roundtrip_preserves_identifier(self):
        plan = mission()
        self.assertEqual(semantic_id(plan), semantic_id(Mission.from_json(plan.to_json())))
        self.assertEqual(len(semantic_id(plan)), 64)

    def test_changed_plan_changes_identifier(self):
        base = semantic_id(mission())
        alternatives = (mission(speed=.3), mission(radius=19), mission(ceiling=4),
                        Mission((Waypoint('b', 0, 0, 1),)),
                        Mission((Waypoint('a', 0, 0, 1, 1),)),
                        Mission((Waypoint('a', 0, 0, 1.001),)))
        for plan in alternatives:
            with self.subTest(plan=plan):
                self.assertNotEqual(semantic_id(plan), base)

    def test_waypoint_order_changes_identifier(self):
        a, b = Waypoint('a', 0, 0, 1), Waypoint('b', 1, 0, 1)
        self.assertNotEqual(semantic_id(Mission((a, b))), semantic_id(Mission((b, a))))

    def test_context_requires_exact_origin_and_revision(self):
        plan = mission()
        bound = bind(plan, 'lab_enu', 7)
        self.assertIs(require_context(bound, 'lab_enu', 7), plan)
        for origin, revision in (('other', 7), ('lab_enu', 8), ('LAB_ENU', 7)):
            with self.subTest(origin=origin, revision=revision), self.assertRaises(ValueError):
                require_context(bound, origin, revision)

    def test_invalid_context_metadata(self):
        for origin in ('', 'a b', '../origin', 'é', 'a' * 65, True):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                bind(mission(), origin, 1)
        for revision in (True, 1.0, '1', -1, 2**31):
            with self.subTest(revision=revision), self.assertRaises(ValueError):
                bind(mission(), 'lab', revision)

    def test_forged_digest_is_refused(self):
        with self.assertRaises(ValueError):
            BoundMission(mission(), MissionContext('lab', 1, '0' * 64))
        for identifier in ('a' * 63, 'A' * 64, 'g' * 64, True):
            with self.subTest(identifier=identifier), self.assertRaises(ValueError):
                MissionContext('lab', 1, identifier)

    def test_binding_cannot_be_accidentally_mutated(self):
        bound = bind(mission(), 'lab', 1)
        with self.assertRaises(FrozenInstanceError):
            bound.context.origin_id = 'other'
        with self.assertRaises(FrozenInstanceError):
            bound.mission = mission(speed=.3)

    def test_unbound_plan_is_refused(self):
        for bad in (None, mission(), {}, True):
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                require_context(bad, 'lab', 1)

    def test_binding_label_is_not_location_proof(self):
        # Deliberate limitation: independently supplied identical labels compare.
        a = bind(mission(), 'caller_asserted_origin', 0)
        b = bind(mission(), 'caller_asserted_origin', 0)
        self.assertEqual(a.context, b.context)
        self.assertIs(require_context(a, 'caller_asserted_origin', 0), a.mission)
