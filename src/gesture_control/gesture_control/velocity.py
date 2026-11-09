"""Offline normalized hand-center to camera-plane velocity; explicit enable."""
import math
from .validation import finite


def hand_velocity(x: float, y: float, enabled: bool = False,
                  limit: float = .2, deadzone: float = .1) -> tuple[float, float]:
    if not finite(limit) or limit <= 0 or not finite(deadzone) or not 0 <= deadzone < 1:
        raise ValueError('invalid mapping configuration')
    if enabled is not True or not all(finite(v) and 0 <= v <= 1 for v in (x, y)):
        return 0., 0.
    def axis(value):
        value = 2 * value - 1
        return math.copysign(max(0., abs(value) - deadzone) / (1 - deadzone), value)
    vx, vy = axis(x), axis(y)
    scale = limit / max(1., math.hypot(vx, vy))
    return vx * scale, vy * scale
