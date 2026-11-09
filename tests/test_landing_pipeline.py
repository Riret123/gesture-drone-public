import sys
from pathlib import Path
from dataclasses import replace
from itertools import permutations
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.landing_observation import ObservationGate, ObservationLimits, TagObservation
from gesture_control.landing_capture import CaptureGate
from gesture_control.landing_candidates import CandidateGate, CandidateFrame
from gesture_control.landing_motion import MotionGate
from gesture_control.landing_pipeline import OfflineLandingPipeline


def pipeline():
    metadata = ObservationGate(7, 'down', 'v1', ObservationLimits(.25, 2, .04, .1, 3))
    candidates = CandidateGate(CaptureGate(metadata, 'a', .25), 3)
    return OfflineLandingPipeline(candidates, MotionGate(1, .125, 1))


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.o = TagObservation(7, 'down', 'v1', 1, (0, 0, 1), 1, .01)
        self.frame = CandidateFrame('a', 0, 1, (self.o,))

    def test_v29_missing_before_acquisition_search_then_valid_descend(self):
        p = pipeline()
        self.assertEqual(p.update(None, .5).proposal.state, 'search')
        result = p.update(self.frame, 1)
        self.assertEqual(result.proposal.state, 'descend')
        self.assertEqual(result.motion_reason, 'anchor_initialized')

    def test_loss_after_acquisition_aborts_and_latches(self):
        p = pipeline()
        p.update(self.frame, 1)
        self.assertEqual(p.update(None, 1.1).proposal.state, 'abort')
        self.assertEqual(p.update(self.frame, 1.2).observation_reason, 'terminal_latched')

    def test_motion_rejection_aborts_without_descent(self):
        p = pipeline()
        p.update(self.frame, 1)
        jump = replace(self.frame, sequence=1, captured_s=1.125,
                       candidates=(replace(self.o, received_s=1.125, position_m=(2, 0, 1)),))
        result = p.update(jump, 1.125)
        self.assertEqual(result.motion_reason, 'innovation_exceeded')
        self.assertEqual(result.proposal.state, 'abort')
        self.assertEqual(result.proposal.descent, 0)

    def test_ambiguity_rejects_before_descent_and_after_acquisition_aborts(self):
        frame = replace(self.frame, candidates=(self.o, self.o))
        p = pipeline()
        self.assertEqual(p.update(frame, 1).proposal.state, 'search')
        p.update(self.frame, 1)
        self.assertEqual(p.update(frame, 1).proposal.state, 'abort')

    def test_v30_candidate_permutations_preserve_valid_and_ambiguous_outcomes(self):
        other = replace(self.o, tag_id=8)
        for candidates in permutations((self.o, other)):
            self.assertEqual(pipeline().update(replace(self.frame, candidates=candidates), 1).proposal.state,
                             'descend')
        for candidates in permutations((self.o, self.o, other)):
            self.assertEqual(pipeline().update(replace(self.frame, candidates=candidates), 1).observation_reason,
                             'target_ambiguous')

    def test_abort_and_invalid_contact_cannot_create_descent(self):
        for kwargs in ({'abort': True}, {'contact': 'yes'}, {'abort': 1}):
            self.assertEqual(pipeline().update(self.frame, 1, **kwargs).proposal.state, 'abort')

    def test_contact_is_explicit_low_pose_evidence_only(self):
        frame = replace(self.frame, candidates=(replace(self.o, position_m=(0, 0, .1)),))
        p = pipeline()
        self.assertEqual(p.update(frame, 1, contact=True).proposal.state, 'touchdown')
        self.assertEqual(p.update(None, 2).proposal.state, 'touchdown')

    def test_capture_replay_cannot_renew_descent(self):
        p = pipeline()
        p.update(self.frame, 1)
        result = p.update(self.frame, 1.1)
        self.assertEqual(result.observation_reason, 'replayed_or_reordered')
        self.assertEqual(result.proposal.state, 'abort')
