"""Offline piecewise-constant source current arithmetic; no thermal model."""
from dataclasses import dataclass
import math
from .validation import finite


@dataclass(frozen=True)
class CurrentSegment:
    duration_s: float
    current_a: float

    def __post_init__(self):
        if not finite(self.duration_s) or self.duration_s <= 0:
            raise ValueError('positive finite duration required')
        if not finite(self.current_a) or self.current_a < 0:
            raise ValueError('nonnegative finite consumption current required')


@dataclass(frozen=True)
class ProfileResult:
    status: str
    duration_s: float | None
    peak_a: float | None
    rms_a: float | None
    energy_j: float | None
    reasons: tuple


def evaluate_profile(segments, source_v: float, peak_limit_a: float,
                     rms_limit_a: float, energy_limit_j: float,
                     *, max_segments: int) -> ProfileResult:
    """Evaluate an explicitly complete, constant-voltage consumption waveform.

    Zero current is a known idle interval. Unknown values and regeneration reject.
    RMS current is a mathematical summary, not proof of temperature/fuse behavior.
    Gaps must be explicit segments; sample timing uncertainty is not modeled.
    """
    if type(max_segments) is not int or max_segments <= 0:
        raise ValueError('positive explicit segment count limit required')
    if not isinstance(segments, (tuple, list)) or not segments:
        raise ValueError('nonempty explicit segment sequence required')
    if len(segments) > max_segments:
        raise ValueError('segment count limit exceeded')
    if any(not isinstance(s, CurrentSegment) for s in segments):
        raise ValueError('validated segments required')
    if not all(finite(v) and v > 0 for v in
               (source_v, peak_limit_a, rms_limit_a, energy_limit_j)):
        raise ValueError('positive finite source and arithmetic limits required')
    try:
        for segment in segments:
            charge_term = segment.duration_s * segment.current_a
            square_term = charge_term * segment.current_a
            if segment.current_a > 0 and (charge_term == 0 or square_term == 0):
                return ProfileResult('INVALID', None, None, None, None, ('arithmetic_underflow',))
        duration = math.fsum(s.duration_s for s in segments)
        charge = math.fsum(s.duration_s * s.current_a for s in segments)
        square_integral = math.fsum(s.duration_s * s.current_a * s.current_a
                                    for s in segments)
        peak = max(s.current_a for s in segments)
        rms = math.sqrt(square_integral / duration)
        energy = source_v * charge
    except (OverflowError, ZeroDivisionError):
        return ProfileResult('INVALID', None, None, None, None, ('arithmetic_overflow',))
    if not all(math.isfinite(v) for v in (duration, charge, square_integral, peak, rms, energy)):
        return ProfileResult('INVALID', None, None, None, None, ('arithmetic_overflow',))
    if charge > 0 and (energy == 0 or rms == 0):
        return ProfileResult('INVALID', None, None, None, None, ('arithmetic_underflow',))
    reasons = ()
    if peak > peak_limit_a:
        reasons += ('peak_exceeded',)
    if rms > rms_limit_a:
        reasons += ('rms_exceeded',)
    if energy > energy_limit_j:
        reasons += ('energy_exceeded',)
    return ProfileResult('EXCEEDS' if reasons else 'WITHIN_ARITHMETIC_LIMITS',
                         duration, peak, rms, energy, reasons)
