"""Offline capture provenance/replay gate layered over observation metadata.

Times must already share one local monotonic clock. This code does not synchronize
clocks or establish that detector-reported capture times are true.
"""
from dataclasses import dataclass
from .landing_observation import ObservationGate, ObservationDecision, TagObservation
from .validation import finite


@dataclass(frozen=True)
class CaptureObservation:
    session_id: str
    sequence: int
    captured_s: float
    observation: TagObservation


class CaptureGate:
    """One explicit session per gate; reject reordering, replay and stale exposure.

    Session identity is not authentication. New sessions require a new gate owned
    by the experiment controller; input data cannot request a reset. Invalid input
    does not consume a sequence number. A clock reversal rejects without resetting.
    """
    def __init__(self, metadata_gate: ObservationGate, session_id: str,
                 max_capture_age_s: float):
        if not isinstance(metadata_gate, ObservationGate):
            raise ValueError('observation gate required')
        if type(session_id) is not str or not session_id or session_id.strip() != session_id:
            raise ValueError('exact nonempty session ID required')
        if not finite(max_capture_age_s) or max_capture_age_s <= 0:
            raise ValueError('positive finite capture age limit required')
        self.metadata_gate = metadata_gate
        self.session_id = session_id
        self.max_capture_age_s = max_capture_age_s
        self._last_sequence = -1
        self._last_capture_s = None
        self._last_now_s = None

    def evaluate(self, capture: CaptureObservation | None,
                 now_s: float) -> ObservationDecision:
        reject = lambda reason: ObservationDecision(False, reason)
        if not finite(now_s) or now_s < 0:
            return reject('invalid_clock')
        if self._last_now_s is not None and now_s < self._last_now_s:
            return reject('clock_reversed')
        self._last_now_s = now_s
        if not isinstance(capture, CaptureObservation):
            return reject('missing_capture')
        c = capture
        if type(c.session_id) is not str or c.session_id != self.session_id:
            return reject('wrong_session')
        if type(c.sequence) is not int or c.sequence < 0:
            return reject('invalid_sequence')
        if c.sequence <= self._last_sequence:
            return reject('replayed_or_reordered')
        if not finite(c.captured_s) or c.captured_s < 0:
            return reject('invalid_capture_time')
        if not isinstance(c.observation, TagObservation):
            return reject('missing_observation')
        if not finite(c.observation.received_s) or c.captured_s > c.observation.received_s:
            return reject('capture_after_receive')
        if self._last_capture_s is not None and c.captured_s <= self._last_capture_s:
            return reject('capture_not_advancing')
        if now_s - c.captured_s > self.max_capture_age_s:
            return reject('exposure_stale')
        result = self.metadata_gate.evaluate(c.observation, now_s)
        if result.accepted:
            self._last_sequence = c.sequence
            self._last_capture_s = c.captured_s
        return result
