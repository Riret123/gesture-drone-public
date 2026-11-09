"""Offline Quest deadman gate: release/lost link inhibits motion immediately."""
import math
from .validation import finite


class Deadman:
    """Tracking recovery requires release then press; stale samples cannot enable."""

    def __init__(self, timeout: float = .25):
        if not finite(timeout) or timeout <= 0:
            raise ValueError('positive timeout required')
        self.timeout = timeout
        self.released = False
        self.clock = -math.inf
        self.sample_clock = -math.inf

    def update(self, pressed: bool, tracking: bool, sample_time: float,
               now: float) -> bool:
        if not finite(now) or now < 0 or now < self.clock:
            self.released = False
            raise ValueError('monotonic time required')
        self.clock = now
        if (type(pressed) is not bool or tracking is not True
                or not finite(sample_time) or sample_time < 0
                or sample_time <= self.sample_clock
                or now < sample_time or now - sample_time >= self.timeout):
            self.released = False
            return False
        self.sample_clock = sample_time
        if not pressed:
            self.released = True
            return False
        return self.released
