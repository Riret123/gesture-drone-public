"""Offline observed-position innovation gate; no trajectory/control output."""
from dataclasses import dataclass
import math
from .validation import finite, vector


@dataclass(frozen=True)
class MotionDecision:
    accepted: bool
    reason: str
    displacement_m: float | None = None


class MotionGate:
    """Require position increments within an explicit relative-speed envelope.

    Includes a fixed allowance for measurement error and a max sample interval.
    A rejected sample does not move the anchor. Reset/reacquisition is explicit.
    This cannot distinguish a slow false target from a true target.
    """
    def __init__(self, max_relative_speed_mps: float, position_allowance_m: float,
                 max_interval_s: float):
        if not all(finite(v) and v > 0 for v in
                   (max_relative_speed_mps, position_allowance_m, max_interval_s)):
            raise ValueError('positive finite offline motion limits required')
        self.max_speed = max_relative_speed_mps
        self.allowance = position_allowance_m
        self.max_interval = max_interval_s
        self._position = None
        self._captured = None

    def evaluate(self, position_m, captured_s: float) -> MotionDecision:
        if not vector(position_m, 3) or not finite(captured_s) or captured_s < 0:
            return MotionDecision(False, 'invalid_sample')
        if self._position is None:
            self._position, self._captured = tuple(position_m), captured_s
            return MotionDecision(True, 'anchor_initialized', 0.)
        interval = captured_s - self._captured
        if interval <= 0:
            return MotionDecision(False, 'capture_not_advancing')
        if interval > self.max_interval:
            return MotionDecision(False, 'reacquisition_required')
        displacement = math.dist(position_m, self._position)
        envelope = self.max_speed * interval + self.allowance
        if not math.isfinite(displacement) or not math.isfinite(envelope):
            return MotionDecision(False, 'arithmetic_overflow')
        if displacement > envelope:
            return MotionDecision(False, 'innovation_exceeded', displacement)
        self._position, self._captured = tuple(position_m), captured_s
        return MotionDecision(True, 'within_motion_envelope', displacement)
