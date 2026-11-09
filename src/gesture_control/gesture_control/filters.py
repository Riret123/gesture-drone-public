"""Scalar filters; instantiate per landmark coordinate; SI monotonic timestamps."""
import math


class EMA:
    def __init__(self, alpha: float = .3):
        if not math.isfinite(alpha) or not 0 < alpha <= 1:
            raise ValueError('alpha must be in (0,1]')
        self.alpha = alpha
        self.value = None

    def update(self, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError('finite sample required')
        self.value = value if self.value is None else self.value + self.alpha * (value - self.value)
        return self.value


class OneEuro:
    def __init__(self, min_cutoff: float = 1., beta: float = .02,
                 derivative_cutoff: float = 1.):
        if (not all(math.isfinite(v) for v in (min_cutoff, beta, derivative_cutoff))
                or min_cutoff <= 0 or beta < 0 or derivative_cutoff <= 0):
            raise ValueError('invalid cutoff')
        self.cutoff, self.beta, self.dcutoff = min_cutoff, beta, derivative_cutoff
        self.previous = self.value = self.time = None
        self.derivative = 0.

    def update(self, value: float, now: float) -> float:
        if not math.isfinite(value) or not math.isfinite(now):
            raise ValueError('finite sample/time required')
        if self.time is None:
            self.previous = self.value = value
            self.time = now
            return value
        dt = now - self.time
        if dt <= 0:
            raise ValueError('strictly increasing time required')
        def alpha(cutoff):
            return 1 / (1 + 1 / (2 * math.pi * cutoff * dt))
        self.derivative += alpha(self.dcutoff) * ((value - self.previous) / dt - self.derivative)
        self.value += alpha(self.cutoff + self.beta * abs(self.derivative)) * (value - self.value)
        self.previous, self.time = value, now
        return self.value
