"""Immutable, thread-safe snapshots with local receive-age expiry."""
from dataclasses import dataclass
import math
import threading


def _finite(value):
    try:
        return (not isinstance(value, bool) and isinstance(value, (int, float))
                and math.isfinite(value))
    except OverflowError:
        return False


@dataclass(frozen=True)
class StateSnapshot:
    connected: bool
    armed: bool
    mode: str = ''
    received_at: float | None = None


class StateWatchdog:
    def __init__(self, clock, max_age=2.0):
        if not _finite(max_age) or max_age <= 0:
            raise ValueError('max_age must be finite and positive')
        self.clock, self.max_age = clock, max_age
        self._lock = threading.Lock()
        self._snapshot = self._received = self._last_clock = None

    def _now(self):
        now = self.clock()
        if (not _finite(now) or now < 0
                or self._last_clock is not None and now < self._last_clock):
            self._snapshot = self._received = None
            return None
        self._last_clock = now
        return now

    def receive(self, message):
        with self._lock:
            now = self._now()
            if (now is None or not isinstance(getattr(message, 'connected', None), bool)
                    or not isinstance(getattr(message, 'armed', None), bool)):
                self._snapshot = self._received = None
                return
            mode = getattr(message, 'mode', '')
            if not isinstance(mode, str) or len(mode) > 64:
                self._snapshot = self._received = None
                return
            self._snapshot = StateSnapshot(message.connected, message.armed, mode, now)
            self._received = now

    def current(self):
        with self._lock:
            now = self._now()
            if (now is None or self._received is None
                    or now - self._received >= self.max_age):
                self._snapshot = self._received = None
            return self._snapshot
