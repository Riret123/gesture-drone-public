"""Offline source leases; no ROS subscriptions or authentication."""
import math
from .validation import finite

PRIORITY = {'voice': 1, 'gesture': 2, 'quest': 3, 'keyboard': 4}
COMMANDS = {'open_palm', 'fist', 'hold', 'land', 'emergency'}


class Arbiter:
    """Emergency and land outrank source priority; expired sources yield hold."""

    def __init__(self, timeout: float = .5):
        if not finite(timeout) or timeout <= 0:
            raise ValueError('positive lease required')
        self.timeout = timeout
        self.entries = {}
        self.clock = -math.inf

    def _time(self, now: float) -> None:
        if not finite(now) or now < 0 or now < self.clock:
            raise ValueError('monotonic finite time required')
        self.clock = now

    def submit(self, source: str, command: str, now: float) -> None:
        if (type(source) is not str or source not in PRIORITY
                or type(command) is not str or command not in COMMANDS):
            raise ValueError('unknown source or command')
        self._time(now)
        self.entries[source] = (command, now)

    def choose(self, now: float) -> str:
        self._time(now)
        active = [(source, command, stamp) for source, (command, stamp)
                  in self.entries.items() if 0 <= now - stamp < self.timeout]
        if not active:
            return 'hold'
        def rank(entry):
            source, command, stamp = entry
            safety = {'emergency': 3, 'land': 2, 'fist': 2, 'hold': 1}.get(command, 0)
            return safety, PRIORITY[source], stamp
        return max(active, key=rank)[1]
