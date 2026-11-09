"""Independent expected paths and resource limits for toy mission trajectories."""
import math
from pathlib import Path
import random
import sys
import unittest
from dataclasses import FrozenInstanceError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

from gesture_control.mission_schema import Mission, Waypoint
from gesture_control.mission_simulation import Trajectory


def plan(*points, speed=1.0):
    return Mission(tuple(points), speed=speed)


class MissionSimulationTests(unittest.TestCase):
    def test_one_leg_independent_distance(self):
        trajectory = Trajectory(plan(Waypoint('a', 3, 4, 0)))
        self.assertEqual(trajectory.duration, 5)
        self.assertEqual(trajectory.distance, 5)
        self.assertEqual(trajectory.at(2.5).position, (1.5, 2, 0))
        self.assertEqual(trajectory.at(2.5).phase, 'travel')

    def test_vertical_leg(self):
        trajectory = Trajectory(plan(Waypoint('a', 0, 0, 2)), start=(0, 0, 1))
        self.assertEqual(trajectory.duration, 1)
        self.assertEqual(trajectory.at(.25).position, (0, 0, 1.25))

    def test_dwell_boundaries(self):
        trajectory = Trajectory(plan(Waypoint('a', 1, 0, 0, 2), Waypoint('b', 2, 0, 0)))
        self.assertEqual(trajectory.at(0).phase, 'travel')
        self.assertEqual(trajectory.at(1).phase, 'dwell')
        self.assertEqual(trajectory.at(2.9).position, (1, 0, 0))
        self.assertEqual(trajectory.at(3).phase, 'travel')
        self.assertEqual(trajectory.at(4).phase, 'complete')

    def test_zero_length_leg_still_dwells(self):
        trajectory = Trajectory(plan(Waypoint('a', 0, 0, 0, 2)))
        self.assertEqual(trajectory.distance, 0)
        self.assertEqual(trajectory.duration, 2)
        self.assertEqual(trajectory.at(0).phase, 'dwell')

    def test_zero_duration_plan(self):
        trajectory = Trajectory(plan(Waypoint('a', 0, 0, 0), Waypoint('b', 0, 0, 0)))
        samples = trajectory.samples(max_samples=1)
        self.assertEqual(len(samples), 1)
        self.assertEqual(samples[0].waypoint, 'b')
        self.assertEqual(samples[0].phase, 'complete')

    def test_past_completion_is_explicit(self):
        trajectory = Trajectory(plan(Waypoint('a', 1, 0, 0)))
        self.assertEqual(trajectory.at(3).position, (1, 0, 0))
        self.assertEqual(trajectory.at(3).time, 3)
        self.assertEqual(trajectory.at(3).phase, 'complete')

    def test_duration_budget_includes_dwell(self):
        for budget in (1, 2.999999):
            with self.subTest(budget=budget), self.assertRaises(ValueError):
                Trajectory(plan(Waypoint('a', 1, 0, 0, 2)), max_duration=budget)
        self.assertEqual(Trajectory(plan(Waypoint('a', 1, 0, 0, 2)), max_duration=3).duration, 3)

    def test_sample_budget_before_allocation(self):
        trajectory = Trajectory(plan(Waypoint('a', 1, 0, 0)))
        with self.assertRaises(ValueError):
            trajectory.samples(interval=.001, max_samples=1000)
        self.assertEqual(len(trajectory.samples(interval=.001, max_samples=1001)), 1001)

    def test_endpoints_unique_for_noninteger_grid(self):
        trajectory = Trajectory(plan(Waypoint('a', 1, 0, 0)))
        samples = trajectory.samples(interval=.3)
        times = [row.time for row in samples]
        self.assertEqual(times[0], 0)
        self.assertEqual(times[-1], 1)
        self.assertEqual(len(times), len(set(times)))
        self.assertEqual(sum(row.phase == 'complete' for row in samples), 1)

    def test_start_must_be_inside_fence(self):
        trajectory_plan = plan(Waypoint('a', 1, 0, 0))
        for start in ((20, 0, 0), (0, 0, 5), (0, 0, -1), (True, 0, 0),
                      (float('nan'), 0, 0), None, (0, 0), ('0', 0, 0)):
            with self.subTest(start=start), self.assertRaises(ValueError):
                Trajectory(trajectory_plan, start=start)

    def test_invalid_parameters(self):
        trajectory_plan = plan(Waypoint('a', 1, 0, 0))
        for bad in (True, None, '1', -1, 0, float('nan'), float('inf')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                Trajectory(trajectory_plan, max_duration=bad)
        trajectory = Trajectory(trajectory_plan)
        for bad in (True, None, '1', -1, float('nan'), float('inf')):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                trajectory.at(bad)
        for bad in (True, 0, 1.0, 100001):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                trajectory.samples(max_samples=bad)

    def test_seeded_paths_stay_inside_convex_fence(self):
        rng = random.Random(12345)
        for run in range(30):
            points = tuple(Waypoint('p' + str(i), rng.uniform(-5, 5),
                                    rng.uniform(-5, 5), rng.uniform(0, 4),
                                    rng.uniform(0, .1)) for i in range(5))
            trajectory = Trajectory(plan(*points))
            samples = trajectory.samples(.25)
            self.assertEqual(trajectory.samples(.25), samples)
            for a, b in zip(samples, samples[1:]):
                self.assertLess(a.time, b.time)
                self.assertLessEqual(math.dist(a.position, b.position), (b.time - a.time) + 1e-12)
                self.assertLess(math.hypot(*b.position[:2]), 20)
                self.assertTrue(0 <= b.position[2] < 5)
            self.assertEqual(samples[-1].position, points[-1].position)

    def test_summary_marks_model_limits(self):
        trajectory = Trajectory(plan(Waypoint('a', 1, 0, 0, 2)))
        metrics = trajectory.summary()
        self.assertIs(metrics['flight_validated'], False)
        self.assertIs(metrics['obstacles_modelled'], False)
        metrics['duration_s'] = -1
        self.assertEqual(trajectory.summary()['duration_s'], 3)

    def test_trajectory_cannot_be_accidentally_reconfigured(self):
        trajectory = Trajectory(plan(Waypoint('a', 1, 0, 0)))
        with self.assertRaises(FrozenInstanceError):
            trajectory.duration = -1
        with self.assertRaises(FrozenInstanceError):
            trajectory.mission = plan(Waypoint('b', 2, 0, 0))

    def test_subnormal_travel_cannot_become_instantaneous(self):
        with self.assertRaises(ValueError):
            Trajectory(plan(Waypoint('a', 5e-324, 0, 0), speed=2))

    def test_subresolution_dwell_cannot_silently_disappear(self):
        with self.assertRaises(ValueError):
            Trajectory(plan(Waypoint('a', 1, 0, 0, 5e-324)))

    def test_tiny_leg_after_large_dwell_is_rejected(self):
        with self.assertRaises(ValueError):
            Trajectory(plan(Waypoint('a', 0, 0, 0, 3600),
                            Waypoint('b', 1e-20, 0, 0)), max_duration=7200)

    def test_binary_lookup_matches_independent_linear_reference(self):
        points = tuple(Waypoint('p' + str(i), (i % 2) * 2, i / 100, 1, .1)
                       for i in range(256))
        trajectory = Trajectory(plan(*points))
        self.assertEqual(trajectory.end_times, tuple(s.end_time for s in trajectory.segments))
        for time in [0] + [s.start_time for s in trajectory.segments] + [
                (s.start_time + s.end_time) / 2 for s in trajectory.segments]:
            expected = next(s for s in trajectory.segments if time < s.end_time)
            sample = trajectory.at(time)
            self.assertEqual(sample.phase, expected.phase)
            self.assertEqual(sample.waypoint, expected.waypoint)
            fraction = (time - expected.start_time) / (expected.end_time - expected.start_time)
            position = tuple(a + fraction * (b - a) for a, b in zip(expected.start, expected.end))
            self.assertEqual(sample.position, position)
