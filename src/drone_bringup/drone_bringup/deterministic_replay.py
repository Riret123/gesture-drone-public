"""In-memory gesture-to-FC simulation: no ROS, camera, sockets or flight physics.

Explicit external safety events model a supervisory input. They do not imply that
live battery/RC telemetry is currently subscribed by the bridge.
"""
import csv
from dataclasses import dataclass
from io import StringIO
from types import SimpleNamespace
from .flight_logic import FlightController
from .state_watchdog import _finite


@dataclass(frozen=True)
class Frame:
    time: float
    hands: tuple


def read_landmark_csv(text):
    try:
        return _read_landmark_csv(text)
    except csv.Error as exc:
        raise ValueError('malformed or oversized CSV field') from exc


def _read_landmark_csv(text):
    """Bounded image-landmark fixtures. Empty frames use hand/index = -1/-1."""
    if not isinstance(text, str) or len(text) > 2_000_000:
        raise ValueError('fixture exceeds text bound')
    reader = csv.DictReader(StringIO(text), strict=True)
    if reader.fieldnames != ['time', 'hand', 'index', 'x', 'y', 'z']:
        raise ValueError('unexpected landmark CSV header')
    groups, previous = {}, -1.
    for row_number, row in enumerate(reader, 1):
        if row_number > 20000 or None in row or any(v is None for v in row.values()):
            raise ValueError('malformed or oversized fixture')
        try:
            stamp, hand, index = float(row['time']), int(row['hand']), int(row['index'])
        except (ValueError, TypeError) as exc:
            raise ValueError('invalid fixture identifiers') from exc
        if not _finite(stamp) or stamp < 0 or stamp < previous:
            raise ValueError('fixture clock must be finite and ordered')
        previous = stamp
        frame = groups.setdefault(stamp, {})
        if hand == index == -1:
            if frame or any(row[key] for key in ('x', 'y', 'z')):
                raise ValueError('empty marker conflicts with hand')
            frame[-1] = None
            continue
        if hand not in (0, 1) or not 0 <= index < 21 or -1 in frame:
            raise ValueError('hand/index outside schema')
        points = frame.setdefault(hand, {})
        if index in points:
            raise ValueError('duplicate landmark')
        try:
            point = tuple(float(row[key]) for key in ('x', 'y', 'z'))
        except ValueError as exc:
            raise ValueError('invalid coordinates') from exc
        if not all(_finite(v) and abs(v) <= 1e6 for v in point):
            raise ValueError('invalid coordinates')
        points[index] = point
    frames = []
    for stamp, hands in groups.items():
        if -1 in hands:
            frames.append(Frame(stamp, ()))
            continue
        if set(hands) not in ({0}, {0, 1}) or any(set(p) != set(range(21)) for p in hands.values()):
            raise ValueError('incomplete hand landmarks')
        frames.append(Frame(stamp, tuple(tuple(points[i] for i in range(21))
                                        for _, points in sorted(hands.items()))))
    return tuple(frames)


class ReplayHarness:
    def __init__(self, frames=2):
        # Imported only by offline harness: live bridge has no gesture dependency.
        from gesture_control.safety import GestureSafety
        self.now = 0.
        self.state = SimpleNamespace(connected=True, armed=False, mode='STABILIZE')
        self.services, self.commands, self.acks = [], [], []
        self.policy = GestureSafety(frames=frames, now=0.)
        self.controller = FlightController(self._service, lambda: self.state,
                                           clock=lambda: self.now)

    def _service(self, operation, value):
        self.services.append((self.now, operation, value))
        if not self.state.connected:
            return False
        if operation == 'set_mode':
            self.state.mode = value
        elif operation == 'arm':
            self.state.armed = value
        elif operation == 'land':
            self.state.mode = 'LAND'
            # Acceptance alone does not imply touchdown or disarming.
        return True

    def command(self, command):
        self.commands.append((self.now, command))
        outcome = self.controller.handle(command)
        self.acks.append((self.now, command, *outcome))
        return outcome

    def frame(self, frame):
        from gesture_control.frame_classifier import classify_frame
        if not isinstance(frame, Frame) or not _finite(frame.time) or frame.time < self.now:
            raise ValueError('replay frame must advance a finite clock')
        self.now = frame.time
        points = [[SimpleNamespace(x=p[0], y=p[1], z=p[2]) for p in hand]
                  for hand in frame.hands]
        command = self.policy.update(classify_frame(points), self.now)
        if command:
            self.command(command)
        self.controller.observe_reset_state()

    def safety_event(self, name):
        if name not in ('rc-loss', 'battery-low', 'fc-link-loss'):
            raise ValueError('unknown fixture safety event')
        if name == 'fc-link-loss':
            self.state.connected = False
        return self.command('emergency')
