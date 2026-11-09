"""Local receive-time freshness gate; no wall-clock or remote timestamp trust."""
import math
from .validation import finite


class Freshness:
    def __init__(self, timeout: float = .5):
        if not finite(timeout) or timeout <= 0:
            raise ValueError('positive timeout required')
        self.timeout = timeout
        self.received = None
        self.clock = -math.inf

    def _check(self, now: float) -> None:
        if not finite(now) or now < 0 or now < self.clock:
            raise ValueError('monotonic finite clock required')
        self.clock = now

    def receive(self, now: float) -> None:
        self._check(now)
        self.received = now

    def fresh(self, now: float) -> bool:
        self._check(now)
        if self.received is None:
            return False
        deadline = self.received + self.timeout
        return finite(deadline) and deadline > self.received and now < deadline
