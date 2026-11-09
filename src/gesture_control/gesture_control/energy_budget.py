"""Offline simultaneous DC rail budget with explicit unknowns; no hardware I/O."""
from dataclasses import dataclass
import math
from .validation import finite


@dataclass(frozen=True)
class RailLoad:
    name: str
    voltage_v: float | None
    continuous_a: float | None
    peak_a: float | None
    efficiency: float | None

    def __post_init__(self):
        if type(self.name) is not str or not self.name.strip() or self.name.strip() != self.name:
            raise ValueError('nonempty exact load name required')
        for field in ('voltage_v', 'continuous_a', 'peak_a', 'efficiency'):
            value = getattr(self, field)
            if value is not None and (not finite(value) or value <= 0):
                raise ValueError('known electrical values must be positive finite numbers')
        if self.efficiency is not None and self.efficiency > 1:
            raise ValueError('efficiency cannot exceed unity')
        if (self.continuous_a is not None and self.peak_a is not None
                and self.peak_a < self.continuous_a):
            raise ValueError('peak demand cannot be below continuous demand')


@dataclass(frozen=True)
class BudgetResult:
    status: str
    continuous_w: float | None
    peak_w: float | None
    continuous_source_a: float | None
    peak_source_a: float | None
    unknown_loads: tuple
    reasons: tuple


def evaluate_budget(loads, source_min_v: float | None,
                    continuous_limit_a: float | None,
                    peak_limit_a: float | None) -> BudgetResult:
    """Sum ALL peaks simultaneously; no duty-cycle diversity assumption.

    The limits must already include owner-reviewed thermal/ambient derating.
    Result only compares arithmetic current demand. It does not select a fuse,
    validate a battery, wiring, transient duration or authorization to energize.
    """
    if not isinstance(loads, (tuple, list)) or not loads:
        raise ValueError('nonempty explicit load list required')
    if any(not isinstance(load, RailLoad) for load in loads):
        raise ValueError('validated load records required')
    if len({load.name for load in loads}) != len(loads):
        raise ValueError('duplicate load names hide accounting mistakes')
    source_values = (source_min_v, continuous_limit_a, peak_limit_a)
    if any(v is not None and (not finite(v) or v <= 0) for v in source_values):
        raise ValueError('known source values must be positive finite numbers')
    if (continuous_limit_a is not None and peak_limit_a is not None
            and peak_limit_a < continuous_limit_a):
        raise ValueError('source peak limit cannot be below continuous limit')
    unknown = tuple(load.name for load in loads if any(
        getattr(load, field) is None
        for field in ('voltage_v', 'continuous_a', 'peak_a', 'efficiency')))
    if unknown or any(v is None for v in source_values):
        reasons = ('missing_load_evidence',) if unknown else ()
        if any(v is None for v in source_values):
            reasons += ('missing_source_evidence',)
        return BudgetResult('UNKNOWN', None, None, None, None, unknown, reasons)
    try:
        for load in loads:
            if load.voltage_v * load.continuous_a == 0 or load.voltage_v * load.peak_a == 0:
                return BudgetResult('INVALID', None, None, None, None, (), ('arithmetic_underflow',))
        continuous = math.fsum(load.voltage_v * load.continuous_a / load.efficiency
                               for load in loads)
        peak = math.fsum(load.voltage_v * load.peak_a / load.efficiency
                         for load in loads)
        current, peak_current = continuous / source_min_v, peak / source_min_v
    except OverflowError:
        return BudgetResult('INVALID', None, None, None, None, (), ('arithmetic_overflow',))
    if not all(math.isfinite(v) for v in (continuous, peak, current, peak_current)):
        return BudgetResult('INVALID', None, None, None, None, (), ('arithmetic_overflow',))
    if any(v == 0 for v in (continuous, peak, current, peak_current)):
        return BudgetResult('INVALID', None, None, None, None, (), ('arithmetic_underflow',))
    reasons = ()
    if current > continuous_limit_a:
        reasons += ('continuous_capacity_exceeded',)
    if peak_current > peak_limit_a:
        reasons += ('peak_capacity_exceeded',)
    return BudgetResult('EXCEEDS' if reasons else 'WITHIN_ARITHMETIC_LIMITS',
                        continuous, peak, current, peak_current, (), reasons)
