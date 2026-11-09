import sys
from pathlib import Path
from dataclasses import replace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.landing_observation import ObservationGate, ObservationLimits, TagObservation
from gesture_control.landing_capture import CaptureGate, CaptureObservation


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.meta = ObservationGate(7, 'down', 'v1', ObservationLimits(.2, 2., .04, .1, 3.))
        self.gate = CaptureGate(self.meta, 'recording-a', .3)
        self.o = TagObservation(7, 'down', 'v1', 1., (0, 0, 1), 1., .01)
        self.c = CaptureObservation('recording-a', 0, .9, self.o)

    def test_v07_old_exposure_with_fresh_receive_rejects(self):
        c = replace(self.c, captured_s=.1)
        self.assertEqual(self.gate.evaluate(c, 1.).reason, 'exposure_stale')
        self.assertTrue(self.gate.evaluate(self.c, 1.).accepted)

    def test_v08_replay_and_reordering(self):
        self.assertTrue(self.gate.evaluate(replace(self.c, sequence=10), 1.).accepted)
        for sequence in (10, 9, 0):
            self.assertEqual(self.gate.evaluate(replace(self.c, sequence=sequence), 1.).reason,
                             'replayed_or_reordered')

    def test_higher_sequence_with_repeated_or_reversed_capture_rejects(self):
        self.assertTrue(self.gate.evaluate(self.c, 1.).accepted)
        for captured in (.9, .8):
            self.assertEqual(self.gate.evaluate(replace(self.c, sequence=1, captured_s=captured), 1.).reason,
                             'capture_not_advancing')

    def test_session_cannot_reset_receiver(self):
        self.assertTrue(self.gate.evaluate(self.c, 1.).accepted)
        wrong = replace(self.c, session_id='new-session', sequence=100)
        self.assertEqual(self.gate.evaluate(wrong, 1.).reason, 'wrong_session')
        valid = replace(self.c, sequence=1, captured_s=.95)
        self.assertTrue(self.gate.evaluate(valid, 1.).accepted)

    def test_invalid_sequence_does_not_consume_state(self):
        for seq in (True, -1, 0., '0', None):
            self.assertEqual(self.gate.evaluate(replace(self.c, sequence=seq), 1.).reason,
                             'invalid_sequence')
        self.assertTrue(self.gate.evaluate(self.c, 1.).accepted)

    def test_invalid_metadata_does_not_consume_sequence(self):
        bad = replace(self.c, observation=replace(self.o, camera_id='wrong'))
        self.assertEqual(self.gate.evaluate(bad, 1.).reason, 'wrong_camera')
        self.assertTrue(self.gate.evaluate(self.c, 1.).accepted)

    def test_time_ordering_and_clock_reversal(self):
        self.assertEqual(self.gate.evaluate(replace(self.c, captured_s=1.01), 1.).reason,
                         'capture_after_receive')
        self.assertTrue(self.gate.evaluate(self.c, 1.).accepted)
        self.assertEqual(self.gate.evaluate(self.c, .99).reason, 'clock_reversed')
        for value in (True, -1, float('inf'), float('nan'), '1'):
            self.assertFalse(self.gate.evaluate(replace(self.c, captured_s=value), 1.).accepted)

    def test_missing_and_invalid_configuration(self):
        self.assertEqual(self.gate.evaluate(None, 1.).reason, 'missing_capture')
        self.assertEqual(self.gate.evaluate(replace(self.c, observation=None), 1.).reason,
                         'missing_observation')
        for age in (True, 0, -1, float('nan'), 10**1000):
            with self.assertRaises(ValueError):
                CaptureGate(self.meta, 'a', age)

    def test_valid_advancing_capture_and_inclusive_age(self):
        self.gate = CaptureGate(self.meta, 'recording-a', .25)
        first = replace(self.c, captured_s=.75)
        self.assertTrue(self.gate.evaluate(first, 1.).accepted)
        second = replace(self.c, sequence=1, captured_s=.95,
                         observation=replace(self.o, received_s=1.1))
        self.assertTrue(self.gate.evaluate(second, 1.1).accepted)
