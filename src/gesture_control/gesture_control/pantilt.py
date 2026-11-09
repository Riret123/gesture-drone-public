"""Offline servo-angle mapping; no PWM or hardware dependencies."""
import math


class PanTilt:
    def __init__(self, minimum: float = 30, maximum: float = 150,
                 alpha: float = .2):
        if (not all(math.isfinite(v) for v in (minimum, maximum, alpha))
                or not 0 <= minimum < maximum <= 180 or not 0 < alpha <= 1):
            raise ValueError('invalid servo configuration')
        self.minimum, self.maximum, self.alpha = minimum, maximum, alpha
        self.angles = ((minimum + maximum) / 2,) * 2

    def update(self, x: float, y: float) -> tuple[float, float]:
        if not all(math.isfinite(v) for v in (x, y)):
            return self.angles
        targets = [self.minimum + max(0, min(1, v)) * (self.maximum - self.minimum)
                   for v in (x, y)]
        self.angles = tuple(old + self.alpha * (new - old)
                            for old, new in zip(self.angles, targets))
        return self.angles
