"""Pure command orchestration. Service adapter returns bool; state is read live."""
import threading
import time
from drone_bringup.state_watchdog import _finite


class FlightController:
    def __init__(self, call, state, takeoff_altitude=2.0, confirm=None,
                 clock=time.monotonic, reset_delay=5.0, startup_latched=False):
        if not _finite(takeoff_altitude) or not 0 < takeoff_altitude <= 2.0:
            raise ValueError('prototype takeoff altitude must be in (0, 2] metres')
        self.takeoff_altitude = takeoff_altitude
        self.call, self.state = call, state
        self.confirm = confirm
        self._takeoff_lock = threading.Lock()
        self._land_lock = threading.Lock()
        self._epoch = 0
        self._safety_active = 0
        self._lock = threading.RLock()
        self._context = threading.local()
        if not _finite(reset_delay) or not 1 <= reset_delay <= 60:
            raise ValueError('reset delay must be in [1,60] seconds')
        self._clock, self._reset_delay = clock, reset_delay
        if type(startup_latched) is not bool:
            raise ValueError('startup_latched must be bool')
        self._landing_latched = startup_latched
        self._disarmed_since = self._last_reset_clock = None
        self._reset_sample_time = None
        self._latch_time = self._clock()

    def latch_landing(self):
        """Reception-time latch, before worker admission or service availability."""
        with self._lock:
            self._landing_latched = True
            self._disarmed_since = None
            self._reset_sample_time = None
            self._latch_time = self._clock()
            self._epoch += 1

    def observe_reset_state(self):
        """Only fresh connected disarmed observations accumulate reset dwell."""
        with self._lock:
            state, now = self.state(), self._clock()
            valid_clock = (_finite(now) and now >= 0 and
                           (self._last_reset_clock is None or now >= self._last_reset_clock))
            if (valid_clock and self._last_reset_clock is not None
                    and now - self._last_reset_clock >= 2.0):
                self._disarmed_since = None
            self._last_reset_clock = now if valid_clock else None
            if (not valid_clock or state is None or state.connected is not True
                    or state.armed is not False):
                self._disarmed_since = None
                self._reset_sample_time = None
                return False
            # Real snapshots carry receive time. Polling a cached snapshot must
            # not manufacture seconds of observed disarm, even if FC max age is
            # configured above the reset dwell. Offline state providers without
            # timestamps treat each invocation as a new observation.
            sample_time = getattr(state, 'received_at', now)
            if (not _finite(sample_time) or not 0 <= now - sample_time < 2.
                    or not _finite(self._latch_time) or sample_time < self._latch_time):
                self._disarmed_since = self._reset_sample_time = None
                return False
            if (self._reset_sample_time is not None
                    and not 0 <= sample_time - self._reset_sample_time < 2.):
                self._disarmed_since = None
            self._reset_sample_time = sample_time
            if self._disarmed_since is None:
                self._disarmed_since = sample_time
            return sample_time - self._disarmed_since >= self._reset_delay

    def operator_reset(self):
        with self._lock:
            ready = self.observe_reset_state()
            if (not ready or self._safety_active or self._takeoff_lock.locked()
                    or self._land_lock.locked()):
                return False, 'reset requires connected disarmed dwell and idle workers'
            self._landing_latched = False
            self._epoch += 1
            return True, 'operator reset confirmed'

    def takeoff_permitted(self):
        """Adapter rechecks after waiting for service, immediately before send.

        This is cooperative cancellation, not an atomic transaction with the FC.
        Already submitted requests cannot be recalled.
        """
        with self._lock:
            if self._landing_latched or getattr(self._context, 'epoch', None) != self._epoch:
                return False
        state = self.state()
        with self._lock:
            return (not self._landing_latched
                    and getattr(self._context, 'epoch', None) == self._epoch
                    and state is not None and state.connected is True)

    def invalidate_takeoff(self):
        """Invalidate synchronously at safety-command reception before dispatch."""
        with self._lock:
            self._epoch += 1

    def hold_permitted(self):
        with self._lock:
            return (getattr(self._context, 'hold_epoch', None) == self._epoch
                    and not self._landing_latched and not self._land_lock.locked())

    def takeoff_ticket(self):
        with self._lock:
            return self._epoch

    def handle(self, command, ticket=None):
        if command == 'operator_reset':
            return self.operator_reset()
        if command in ('fist', 'land', 'emergency'):
            self.latch_landing()
        if command in ('fist', 'land', 'emergency', 'hold'):
            with self._lock:
                if command == 'hold' and ticket is not None and ticket != self._epoch:
                    return False, 'hold superseded by newer safety command'
                if command == 'hold' and self._landing_latched:
                    return False, 'hold blocked by landing latch'
                self._epoch += 1
                self._safety_active += 1
                if command == 'hold':
                    self._context.hold_epoch = self._epoch
            try:
                return self._handle_safety(command)
            finally:
                if command == 'hold':
                    self._context.hold_epoch = None
                with self._lock:
                    self._safety_active -= 1
        if command != 'open_palm':
            return True, 'no action'
        if not self._takeoff_lock.acquire(blocking=False):
            return True, 'takeoff=SKIP(in progress)'
        try:
            with self._lock:
                if self._landing_latched:
                    return False, 'takeoff blocked by landing latch; operator reset required'
                if self._safety_active:
                    return False, 'takeoff blocked by safety command in progress'
                if ticket is not None and ticket != self._epoch:
                    return False, 'takeoff cancelled before worker execution'
                epoch = self._epoch
                self._context.epoch = epoch
            state = self.state()
            if (state is None or state.connected is not True
                    or not isinstance(state.armed, bool)):
                return False, 'state unavailable or disconnected'
            steps = []
            operations = [('set_mode', 'GUIDED')]
            if not state.armed:
                operations.append(('arm', True))
            else:
                steps.append('arm=SKIP(already armed)')
            operations.append(('takeoff', self.takeoff_altitude))
            for name, value in operations:
                with self._lock:
                    if epoch != self._epoch:
                        return False, '; '.join(steps + ['cancelled by safety command'])
                state = self.state()
                if state is None or state.connected is not True:
                    return False, '; '.join(steps + ['state unavailable or disconnected'])
                with self._lock:
                    if epoch != self._epoch or self._landing_latched:
                        return False, '; '.join(steps + ['cancelled during state read'])
                if not self.call(name, value):
                    return False, '; '.join(steps + [name + '=FAIL'])
                if name in ('set_mode', 'arm') and self.confirm is not None:
                    if not self.confirm(name, value):
                        return False, '; '.join(steps + [name + '=UNCONFIRMED'])
                label = f'takeoff({self.takeoff_altitude}m)' if name == 'takeoff' else name
                steps.append(label + '=OK')
            return True, '; '.join(steps)
        finally:
            self._context.epoch = None
            self._takeoff_lock.release()

    def _handle_safety(self, command):
        if command == 'hold':
            if self._land_lock.locked():
                return False, 'hold blocked by landing in progress'
            state = self.state()
            if (state is not None and state.connected is True and state.armed is False
                    and not self._takeoff_lock.locked()):
                return True, 'hold=SKIP(disarmed)'
            return self.call('set_mode', 'LOITER'), 'set_mode(LOITER)'
        if not self._land_lock.acquire(blocking=False):
            return True, 'land=SKIP(in progress)'
        try:
            state = self.state()
            if (state is not None and state.connected is True and state.armed is False
                    and not self._takeoff_lock.locked()):
                return True, 'land=SKIP(disarmed)'
            ok = self.call('land', None)
            return ok, 'land=' + ('OK' if ok else 'FAIL')
        finally:
            self._land_lock.release()
