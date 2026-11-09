import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.landing_motion import MotionGate


class MotionTests(unittest.TestCase):
    def setUp(self):
        self.gate = MotionGate(1., .125, 1.)

    def test_v16_pose_jump_rejects_without_moving_anchor(self):
        self.assertTrue(self.gate.evaluate((0, 0, 1), 1).accepted)
        self.assertEqual(self.gate.evaluate((10, 0, 1), 1.5).reason, 'innovation_exceeded')
        self.assertTrue(self.gate.evaluate((.25, 0, 1), 1.5).accepted)

    def test_stationary_and_exact_envelope(self):
        self.gate.evaluate((0, 0, 1), 1)
        self.assertTrue(self.gate.evaluate((.625, 0, 1), 1.5).accepted)
        self.assertTrue(self.gate.evaluate((.625, 0, 1), 2).accepted)

    def test_gap_requires_new_gate_not_automatic_reacquisition(self):
        self.gate.evaluate((0, 0, 1), 1)
        self.assertEqual(self.gate.evaluate((0, 0, 1), 3).reason, 'reacquisition_required')
        self.assertEqual(self.gate.evaluate((0, 0, 1), 4).reason, 'reacquisition_required')

    def test_time_replay_and_invalid_sample(self):
        self.gate.evaluate((0, 0, 1), 1)
        for stamp in (1, .9):
            self.assertEqual(self.gate.evaluate((0, 0, 1), stamp).reason, 'capture_not_advancing')
        for position in ((True, 0, 1), (float('nan'), 0, 1), None):
            self.assertEqual(self.gate.evaluate(position, 2).reason, 'invalid_sample')

    def test_mutable_input_is_copied(self):
        position = [0, 0, 1]
        self.gate.evaluate(position, 1)
        position[0] = 100
        self.assertTrue(self.gate.evaluate((0, 0, 1), 1.5).accepted)

    def test_numeric_overflow_and_invalid_configuration(self):
        self.gate.evaluate((-1e308, 0, 1), 1)
        self.assertEqual(self.gate.evaluate((1e308, 0, 1), 1.5).reason, 'arithmetic_overflow')
        for value in (0, True, float('nan'), 10**1000):
            with self.assertRaises(ValueError):
                MotionGate(value, .1, 1)
