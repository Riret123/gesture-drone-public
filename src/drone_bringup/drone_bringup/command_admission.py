"""Bound worker admission with a reserved landing lane and no command queue."""
import threading


class CommandAdmission:
    def __init__(self):
        self._lock = threading.Lock()
        self._leases = {}

    def is_idle(self):
        """Include admitted workers that have not entered controller code yet."""
        with self._lock:
            return not self._leases

    def acquire(self, command):
        if not isinstance(command, str):
            return None
        if command in ('fist', 'land', 'emergency'):
            lane = 'land'
        elif command == 'hold':
            lane = 'hold'
        elif command == 'open_palm':
            lane = 'takeoff'
        else:
            return None
        with self._lock:
            if lane in self._leases:
                return None
            if lane == 'hold' and 'land' in self._leases:
                return None
            if lane == 'takeoff' and ('land' in self._leases or 'hold' in self._leases):
                return None
            lease = object()
            self._leases[lane] = lease
            return lease

    def release(self, lease):
        with self._lock:
            for lane, current in tuple(self._leases.items()):
                if current is lease:
                    del self._leases[lane]
                    return
