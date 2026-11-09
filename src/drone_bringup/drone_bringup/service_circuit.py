"""Bounded per-operation circuit; uncertain actuation is never retried."""
import threading


class ServiceCircuit:
    """Three failures block an operation until explicit process/operator recovery.

    Landing has its own circuit so an arm failure cannot consume landing capacity.
    No automatic half-open actuation probe is permitted.
    """

    def __init__(self, threshold=3):
        if type(threshold) is not int or not 1 <= threshold <= 10:
            raise ValueError('failure threshold must be an integer in [1,10]')
        self.threshold = threshold
        self._failures = {}
        self._active = set()
        self._lock = threading.Lock()

    def run(self, operation, callback):
        with self._lock:
            if (self._failures.get(operation, 0) >= self.threshold
                    or operation in self._active):
                return False
            self._active.add(operation)
        ok = False
        try:
            ok = callback() is True
        except Exception:
            ok = False
        finally:
            with self._lock:
                self._active.discard(operation)
                # Success must not erase uncertainty from an earlier failure.
                if not ok:
                    self._failures[operation] = self._failures.get(operation, 0) + 1
        return ok
