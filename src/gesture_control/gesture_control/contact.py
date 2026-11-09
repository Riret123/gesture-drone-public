"""Offline contact evidence debounce; never commands disarm."""
import math
from .validation import finite


class ContactConfirmation:
    def __init__(self, dwell: float = .3, max_height: float = .15):
        if (not all(finite(v) for v in (dwell, max_height))
                or dwell <= 0 or max_height <= 0):
            raise ValueError('positive limits required')
        self.dwell, self.max_height = dwell, max_height
        self.start = None
        self.clock = -math.inf

    def update(self, contact: bool, height: float, now: float) -> bool:
        if not finite(now) or now < 0 or now < self.clock:
            raise ValueError('monotonic finite time required')
        self.clock = now
        if contact is not True or not finite(height) or not 0 <= height <= self.max_height:
            self.start = None
            return False
        if self.start is None:
            self.start = now
        deadline = self.start + self.dwell
        return finite(deadline) and deadline > self.start and now >= deadline
