"""Offline planar acceleration limiter; explicit stop bypasses smoothing."""
import math
from .validation import finite, vector


def _cap(value, bound):
    """Preserve direction without dividing a huge norm by a tiny bound."""
    maximum = max(abs(v) for v in value)
    if maximum == 0:
        return tuple(value)
    direction = tuple(v / maximum for v in value)
    norm = math.hypot(*direction)
    if maximum <= bound / norm:
        return tuple(value)
    return tuple(v / norm * bound for v in direction)


class SlewLimiter:
    def __init__(self, acceleration: float = .3, speed: float = .2):
        if (not all(finite(v) for v in (acceleration, speed))
                or acceleration <= 0 or speed <= 0):
            raise ValueError('positive bounds required')
        self.acceleration, self.speed = acceleration, speed
        self.value = (0., 0.)

    def update(self, target: tuple, dt: float, stop: bool = False) -> tuple:
        if type(stop) is not bool:
            raise ValueError('stop must be an exact boolean')
        if stop:
            self.value = (0., 0.)
            return self.value
        if not vector(target, 2) or not finite(dt) or not 0 < dt <= 1:
            raise ValueError('finite target and dt in (0,1] required')
        step = self.acceleration * dt
        if not finite(step) or step <= 0:
            raise ValueError('acceleration step is not representable')
        target = _cap(target, self.speed)
        delta = tuple(t - v for t, v in zip(target, self.value))
        if not vector(delta, 2):
            raise ValueError('velocity change is not representable')
        increment = _cap(delta, step)
        updated = tuple(v + d for v, d in zip(self.value, increment))
        if not vector(updated, 2):
            raise ValueError('updated velocity is not representable')
        self.value = updated
        return self.value
