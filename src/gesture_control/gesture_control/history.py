"""Bounded in-memory telemetry history for a future read-only adapter."""
from collections import deque
import math
from .validation import finite


class TelemetryHistory:
    def __init__(self, capacity: int = 30):
        if type(capacity) is not int or not 1 <= capacity <= 1000:
            raise ValueError('capacity must be integer 1..1000')
        self.acks = deque(maxlen=capacity)
        self.sample = None
        self.received = None
        self.clock = -math.inf

    def ack(self, text: str) -> None:
        if not isinstance(text, str) or len(text) > 256:
            raise ValueError('ack must be text <=256 characters')
        self.acks.append(text)

    def _time(self, now: float) -> None:
        if not finite(now) or now < 0 or now < self.clock:
            raise ValueError('monotonic finite time required')
        self.clock = now

    def update(self, mode: str, battery: float, deadman: bool, now: float) -> None:
        if (not isinstance(mode, str) or len(mode) > 64
                or not finite(battery)
                or not 0 <= battery <= 100 or type(deadman) is not bool):
            raise ValueError('invalid telemetry')
        self._time(now)
        self.sample = dict(mode=mode, battery=battery, deadman=deadman)
        self.received = now

    def snapshot(self, now: float) -> dict:
        self._time(now)
        return dict(self.sample or dict(mode=None, battery=None, deadman=None),
                    age=None if self.received is None else now - self.received,
                    acks=list(self.acks), mock=False)
