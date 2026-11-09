"""Bounded single-frame tag candidate selection; ambiguous target means reject."""
from dataclasses import dataclass
from .landing_capture import CaptureGate, CaptureObservation
from .landing_observation import TagObservation, ObservationDecision
from .validation import finite


@dataclass(frozen=True)
class CandidateFrame:
    session_id: str
    sequence: int
    captured_s: float
    candidates: tuple


class CandidateGate:
    """Select exactly one expected tag from a bounded same-camera frame.

    Other valid tag IDs may coexist. Multiple expected-tag detections reject even
    if their poses agree; first/best-wins would hide physical ambiguity. Candidate
    count is checked before iteration. No detector or confidence ranking supplied.
    """
    def __init__(self, capture_gate: CaptureGate, max_candidates: int):
        if not isinstance(capture_gate, CaptureGate):
            raise ValueError('capture gate required')
        if type(max_candidates) is not int or max_candidates <= 0:
            raise ValueError('positive explicit candidate bound required')
        self.capture_gate = capture_gate
        self.max_candidates = max_candidates
        self._last_now_s = None

    def evaluate(self, frame: CandidateFrame | None, now_s: float) -> ObservationDecision:
        reject = lambda reason: ObservationDecision(False, reason)
        if not finite(now_s) or now_s < 0:
            return reject('invalid_clock')
        if self._last_now_s is not None and now_s < self._last_now_s:
            return reject('clock_reversed')
        self._last_now_s = now_s
        if not isinstance(frame, CandidateFrame):
            return reject('missing_frame')
        if type(frame.candidates) is not tuple:
            return reject('invalid_candidate_container')
        if len(frame.candidates) > self.max_candidates:
            return reject('too_many_candidates')
        metadata = self.capture_gate.metadata_gate
        expected = []
        received = None
        for candidate in frame.candidates:
            if not isinstance(candidate, TagObservation):
                return reject('invalid_candidate')
            if type(candidate.tag_id) is not int or candidate.tag_id < 0:
                return reject('invalid_candidate_id')
            if not finite(candidate.received_s) or candidate.received_s < 0:
                return reject('invalid_candidate_receive_time')
            if candidate.camera_id != metadata.camera_id:
                return reject('mixed_camera_frame')
            if candidate.calibration_id != metadata.calibration_id:
                return reject('mixed_calibration_frame')
            if received is None:
                received = candidate.received_s
            elif candidate.received_s != received:
                return reject('mixed_receive_times')
            if candidate.tag_id == metadata.tag_id:
                expected.append(candidate)
        if not expected:
            return reject('target_absent')
        if len(expected) != 1:
            return reject('target_ambiguous')
        capture = CaptureObservation(frame.session_id, frame.sequence, frame.captured_s, expected[0])
        return self.capture_gate.evaluate(capture, now_s)
