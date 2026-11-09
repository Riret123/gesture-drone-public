"""Pure receive-time observation contract for isolated SITL acceptance only."""
from dataclasses import dataclass
import math
from .state_watchdog import _finite


@dataclass(frozen=True)
class ObservationLimits:
    max_age_sec: float = 2.
    dwell_sec: float = 2.
    target_m: float = 2.
    altitude_tolerance_m: float = .25
    position_tolerance_m: float = .3
    rc_mode: str = 'LAND'

    def __post_init__(self):
        numeric = (self.max_age_sec, self.dwell_sec, self.target_m,
                   self.altitude_tolerance_m, self.position_tolerance_m)
        if (not all(_finite(v) and v > 0 for v in numeric)
                or self.target_m > 2 or self.altitude_tolerance_m >= self.target_m
                or self.rc_mode not in ('LAND', 'RTL', 'SMART_RTL')):
            raise ValueError('invalid explicit SITL observation limits')


class ScenarioObservations:
    def __init__(self, limits=None):
        self.limits = limits if limits is not None else ObservationLimits()
        if not isinstance(self.limits, ObservationLimits):
            raise ValueError('limits must be ObservationLimits')
        self._samples = {}
        self._clock = None
        self._position_sequence = 0
        self._hold = None
        self._fault_time = None

    def _now(self, now):
        if (not _finite(now) or now < 0
                or self._clock is not None and now < self._clock):
            self._samples.clear()
            self._hold = None
            self._fault_time = None
            return False
        if self._clock is not None and now-self._clock >= self.limits.max_age_sec:
            self._hold = None
        self._clock = now
        return True

    def mark_rc_fault(self, now):
        """Call only after an acknowledged simulator fault injection."""
        if self._now(now):
            self._fault_time = now

    def _record(self, name, value, now, valid):
        if not self._now(now):
            return
        if not valid:
            self._samples.pop(name, None)
            self._hold = None
            return
        old = self._samples.get(name)
        if old is not None and now-old[1] >= self.limits.max_age_sec:
            self._hold = None
        if name == 'position' and (old is None or now > old[1]):
            self._position_sequence += 1
        self._samples[name] = (value, now)

    def update_state(self, connected, armed, mode, now):
        self._record('state', (connected, armed, mode), now,
                     type(connected) is bool and type(armed) is bool
                     and isinstance(mode, str) and 0 < len(mode) <= 64)

    def update_altitude(self, altitude, now):
        self._record('altitude', altitude, now, _finite(altitude))

    def update_landed(self, landed, now):
        self._record('landed', landed, now, type(landed) is int and landed in (1, 2, 3, 4))

    def update_position(self, position, now):
        valid = (isinstance(position, (tuple, list)) and len(position) == 3
                 and all(_finite(v) and abs(v) <= 1e6 for v in position))
        self._record('position', tuple(position) if valid else None, now, valid)

    def _fresh(self, name, now):
        value = self._samples.get(name)
        if value is None or not 0 <= now-value[1] < self.limits.max_age_sec:
            return None
        return value[0]

    def ready(self, condition, now):
        if condition not in ('connected_disarmed', 'landed_disarmed',
                             'airborne_at_target', 'loiter_stable', 'configured_rc_failsafe'):
            raise ValueError('unknown observation condition')
        if not self._now(now):
            return False
        state = self._fresh('state', now)
        altitude = self._fresh('altitude', now)
        landed = self._fresh('landed', now)
        if state is None or state[0] is not True:
            self._hold = None
            return False
        _, armed, mode = state
        if condition == 'configured_rc_failsafe':
            return (self._fault_time is not None
                    and self._samples['state'][1] > self._fault_time
                    and mode == self.limits.rc_mode)
        if condition in ('connected_disarmed', 'landed_disarmed'):
            return (not armed and landed == 1 and altitude is not None
                    and abs(altitude) <= self.limits.altitude_tolerance_m)
        airborne = (armed and landed == 2 and altitude is not None
                    and abs(altitude-self.limits.target_m) <= self.limits.altitude_tolerance_m)
        if condition == 'airborne_at_target':
            return airborne and mode == 'GUIDED'
        position = self._fresh('position', now)
        if not airborne or mode != 'LOITER' or position is None:
            self._hold = None
            return False
        if self._hold is None or math.dist(position, self._hold[0]) > self.limits.position_tolerance_m:
            self._hold = (position, now, self._position_sequence, 1)
            return False
        anchor, start, sequence, count = self._hold
        if sequence != self._position_sequence:
            count += 1
        self._hold = (anchor, start, self._position_sequence, count)
        return now-start >= self.limits.dwell_sec and count >= 3
