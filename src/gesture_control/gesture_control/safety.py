"""Camera-independent gesture safety policy; timestamps are monotonic seconds."""
import math


def _finite_time(value):
    try:
        return (not isinstance(value, bool) and isinstance(value, (int, float))
                and math.isfinite(value) and value >= 0)
    except OverflowError:
        return False


class GestureDebouncer:
    def __init__(self, frames=5):
        if isinstance(frames, bool) or not isinstance(frames, int) or frames < 1:
            raise ValueError('frames must be a positive integer')
        self.frames = frames
        self.reset()

    def reset(self):
        self.candidate = None
        self.count = 0

    def update(self, gesture):
        if gesture is None:
            self.reset()
            return None
        self.count = self.count + 1 if gesture == self.candidate else 1
        self.candidate = gesture
        return gesture if self.count >= self.frames else None


def detect_emergency(gestures):
    return list(gestures).count('fist') >= 2


class GestureSafety:
    def __init__(self, frames=5, hold_after=2.0, land_after=5.0, now=0.0):
        if not all(_finite_time(x) for x in (hold_after, land_after, now)):
            raise ValueError('times must be finite')
        if not 0 < hold_after < land_after:
            raise ValueError('require 0 < hold_after < land_after')
        self.debouncer = GestureDebouncer(frames)
        self.hold_after, self.land_after = hold_after, land_after
        self.last_valid = self.last_time = now
        self.last_output = None

    def update(self, gestures, now):
        if not _finite_time(now) or now < self.last_time:
            raise ValueError('timestamps must be finite and monotonic')
        repeated_time = now == self.last_time
        if now - self.last_time >= self.hold_after:
            self.debouncer.reset()
        self.last_time = now
        if (not isinstance(gestures, (tuple, list)) or len(gestures) > 2
                or any(not isinstance(g, str) for g in gestures)):
            gestures = []
        else:
            gestures = list(gestures)
        if repeated_time and self.debouncer.count and not detect_emergency(gestures):
            return None
        if detect_emergency(gestures):
            self.debouncer.reset()
            command = 'emergency'
        else:
            # Mixed or unrecognized hands cannot renew the valid-input lease.
            raw = gestures[0] if gestures and len(set(gestures)) == 1 else None
            raw = raw if raw in ('fist', 'open_palm') else None
            command = self.debouncer.update(raw)
            if command:
                self.last_valid = now
            elapsed = now - self.last_valid
            if command is None:
                command = ('land' if elapsed >= self.land_after else
                           'hold' if elapsed >= self.hold_after else None)
        if command is None or command == self.last_output:
            return None
        self.last_output = command
        return command
