"""Crossings, delayed occupancy and independent dense/metamorphic checks."""
import math
from pathlib import Path
import random
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.mission_binding import bind
from gesture_control.mission_schema import Mission, Waypoint
from gesture_control.swarm_separation import AgentPlan, assess_fleet, closest_approach


def agent(name, start, end, speed=1, delay=0, origin='lab', revision=1):
    mission = Mission((Waypoint('target', *end),), speed=speed)
    return AgentPlan(name, bind(mission, origin, revision), start, delay)


class SwarmSeparationTests(unittest.TestCase):
    def test_perpendicular_crossing_between_ticks(self):
        a = agent('a', (-1, 0, 1), (1, 0, 1))
        b = agent('b', (0, -1, 1), (0, 1, 1))
        self.assertGreater(math.dist(a.position_at(0), b.position_at(0)), 1)
        self.assertGreater(math.dist(a.position_at(2), b.position_at(2)), 1)
        result = closest_approach(a, b, 2)
        self.assertAlmostEqual(result.time, 1, places=12)
        self.assertAlmostEqual(result.distance, 0, places=12)

    def test_head_on_paths(self):
        a = agent('a', (-2, 0, 1), (2, 0, 1))
        b = agent('b', (2, 0, 1), (-2, 0, 1))
        result = closest_approach(a, b, 4)
        self.assertEqual(result.time, 2)
        self.assertEqual(result.distance, 0)

    def test_parallel_paths_constant_distance_earliest_time(self):
        a = agent('a', (-2, 0, 1), (2, 0, 1))
        b = agent('b', (-2, 1, 1), (2, 1, 1))
        result = closest_approach(a, b, 4)
        self.assertEqual(result.time, 0)
        self.assertEqual(result.distance, 1)

    def test_vertical_separation_is_three_dimensional(self):
        a = agent('a', (-1, 0, 1), (1, 0, 1))
        b = agent('b', (0, -1, 3), (0, 1, 3))
        result = closest_approach(a, b, 2)
        self.assertEqual(result.distance, 2)
        self.assertAlmostEqual(result.time, 1, places=12)

    def test_prestart_agent_occupies_start(self):
        a = agent('a', (-1, 0, 1), (1, 0, 1))
        b = agent('b', (0, 0, 1), (0, 2, 1), delay=10)
        result = closest_approach(a, b, 2)
        self.assertEqual(result.distance, 0)
        self.assertEqual(result.time, 1)

    def test_finished_agent_occupies_endpoint(self):
        a = agent('a', (-1, 0, 1), (0, 0, 1))
        b = agent('b', (0, 3, 1), (0, -1, 1))
        result = closest_approach(a, b, 4)
        self.assertEqual(result.distance, 0)
        self.assertEqual(result.time, 3)

    def test_horizon_clips_future_collision(self):
        a = agent('a', (-2, 0, 1), (2, 0, 1))
        b = agent('b', (2, 0, 1), (-2, 0, 1))
        result = closest_approach(a, b, 1)
        self.assertEqual(result.distance, 2)
        self.assertEqual(result.time, 1)

    def test_swapping_agents_preserves_metrics(self):
        a = agent('a', (-2, 0, 1), (2, 0, 1))
        b = agent('b', (0, -1, 2), (0, 3, 2))
        ab, ba = closest_approach(a, b, 4), closest_approach(b, a, 4)
        self.assertEqual(ab.distance, ba.distance)
        self.assertEqual(ab.time, ba.time)

    def test_common_translation_preserves_separation(self):
        a = agent('a', (-2, 0, 1), (2, 0, 1))
        b = agent('b', (0, -1, 2), (0, 3, 2))
        shifted_a = agent('a', (1, 2, 1.5), (5, 2, 1.5))
        shifted_b = agent('b', (3, 1, 2.5), (3, 5, 2.5))
        before, after = closest_approach(a, b, 4), closest_approach(shifted_a, shifted_b, 4)
        self.assertAlmostEqual(before.distance, after.distance)
        self.assertAlmostEqual(before.time, after.time)

    def test_context_mismatch_is_not_comparable(self):
        a = agent('a', (0, 0, 1), (1, 0, 1))
        for origin, revision in (('other', 1), ('lab', 2)):
            b = agent('b', (0, 1, 1), (1, 1, 1), origin=origin, revision=revision)
            with self.subTest(origin=origin, revision=revision), self.assertRaises(ValueError):
                closest_approach(a, b, 2)

    def test_fleet_conflict_includes_threshold(self):
        a = agent('a', (-2, 0, 1), (2, 0, 1))
        b = agent('b', (-2, 1, 1), (2, 1, 1))
        self.assertTrue(assess_fleet([a, b], 4, 1)['conflict'])
        self.assertFalse(assess_fleet([a, b], 4, .999)['conflict'])
        self.assertIs(assess_fleet([a, b], 4, .999)['flight_validated'], False)

    def test_invalid_fleets_and_parameters(self):
        a = agent('a', (0, 0, 1), (1, 0, 1))
        b = agent('b', (0, 1, 1), (1, 1, 1))
        for fleet in ([], [a], [a, a], [a, None], [a] * 33, None):
            with self.subTest(fleet=type(fleet)), self.assertRaises(ValueError):
                assess_fleet(fleet, 2, 1)
        for bad in (True, 0, -1, float('nan'), float('inf'), '1'):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess_fleet([a, b], bad, 1)
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                assess_fleet([a, b], 2, bad)

    def test_dense_oracle_never_beats_continuous_minimum(self):
        rng = random.Random(7742)
        for run in range(20):
            positions = [tuple(rng.uniform(-3, 3) for _ in range(2)) + (1.0,)
                         for _ in range(4)]
            a = agent('a', positions[0], positions[1], delay=rng.random())
            b = agent('b', positions[2], positions[3], delay=rng.random())
            result = closest_approach(a, b, 10)
            observed = min(math.dist(a.position_at(t / 100), b.position_at(t / 100))
                           for t in range(1001))
            self.assertLessEqual(result.distance, observed + 1e-10)
            self.assertAlmostEqual(result.distance,
                                   math.dist(a.position_at(result.time), b.position_at(result.time)), places=10)

    def test_global_delay_cannot_erase_positive_interval(self):
        with self.assertRaises(ValueError):
            agent('a', (0, 0, 1), (1e-20, 0, 1), delay=100)

    def test_invalid_agent_identity_and_delay(self):
        plan = bind(Mission((Waypoint('a', 1, 0, 1),)), 'lab', 1)
        for name in ('', '../a', 'a b', 'a' * 33, True):
            with self.subTest(name=name), self.assertRaises(ValueError):
                AgentPlan(name, plan)
        for delay in (True, -1, float('nan'), float('inf'), '1', 86401):
            with self.subTest(delay=delay), self.assertRaises(ValueError):
                AgentPlan('a', plan, delay=delay)

    def test_mutable_start_input_is_copied(self):
        start = [0, 0, 1]
        a = agent('a', start, (1, 0, 1), delay=2)
        start[0] = 9
        self.assertEqual(a.position_at(0), (0, 0, 1))

    def test_stationary_agent_zero_duration_occupancy(self):
        a = agent('a', (0, 0, 1), (0, 0, 1))
        b = agent('b', (-1, 0, 1), (1, 0, 1))
        result = closest_approach(a, b, 2)
        self.assertAlmostEqual(result.distance, 0)
        self.assertAlmostEqual(result.time, 1)

    def test_breakpoints_include_delayed_dwell_end(self):
        plan = Mission((Waypoint('a', 1, 0, 1, 2), Waypoint('b', 2, 0, 1)), speed=1)
        a = AgentPlan('a', bind(plan, 'lab', 1), (0, 0, 1), delay=3)
        self.assertEqual(a.breakpoints(10), (0, 3, 4, 6, 7, 10))
