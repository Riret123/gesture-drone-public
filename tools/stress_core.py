"""Sustained seeded offline command/geometry and real-thread cancellation campaign.

No ROS, camera, MAVROS, sockets, serial ports or physical actuation. Output is
aggregate evidence only. A pass is not exhaustive verification or flight approval.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import random
import sys
import threading
import time
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'src/gesture_control'), str(ROOT / 'src/drone_bringup')]
from drone_bringup.flight_logic import FlightController
from drone_bringup.state_watchdog import StateWatchdog
from gesture_control.gesture_classifier import classify_gesture

SOURCES = ('src/drone_bringup/drone_bringup/flight_logic.py',
           'src/drone_bringup/drone_bringup/flight_cmd_bridge.py',
           'src/drone_bringup/drone_bringup/state_watchdog.py',
           'src/drone_bringup/drone_bringup/service_circuit.py',
           'src/gesture_control/gesture_control/gesture_classifier.py',
           'src/gesture_control/gesture_control/safety.py',
           'src/gesture_control/gesture_control/gesture_node.py')


def manifest():
    return {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in SOURCES}


class Campaign:
    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.cases = self.commands = self.geometry = self.thread_trials = 0

    def case(self):
        rng = self.rng
        now = [0.]
        state = SimpleNamespace(connected=True, armed=False, mode='STABILIZE')
        guard = StateWatchdog(lambda: now[0], max_age=rng.choice((.5, 2., 10.)))
        expected_latch = [True]
        def service(operation, value):
            if (operation in ('arm', 'takeoff') or (operation, value) == ('set_mode', 'GUIDED')):
                if expected_latch[0]:
                    raise AssertionError('actuation submitted while independent model is latched')
            if rng.random() < .03:
                raise RuntimeError('synthetic service exception')
            accepted = rng.random() >= .1
            if accepted and operation == 'arm':
                state.armed = True
            if accepted and operation == 'set_mode':
                state.mode = value
            return accepted
        logic = FlightController(service, guard.current, clock=lambda: now[0], startup_latched=True)
        commands = ('open_palm', 'fist', 'land', 'emergency', 'hold', 'other',
                    'operator_reset', 'arm', 'takeoff', 'unknown')
        for index in range(100):
            now[0] += rng.uniform(.001, .4)
            state.connected, state.armed = rng.random() > .1, rng.random() > .5
            guard.receive(state)
            if index % 23 == 0:
                state.connected, state.armed = True, False
                for _ in range(6):
                    now[0] += 1.
                    guard.receive(state)
                    logic.observe_reset_state()
            if rng.random() < .1:
                now[0] += rng.choice((2., 5., 11.))
            command = rng.choice(commands)
            if command in ('fist', 'land', 'emergency'):
                expected_latch[0] = True
            try:
                ok, _ = logic.handle(command)
            except RuntimeError:
                ok = False
            if command == 'operator_reset' and ok:
                expected_latch[0] = False
            self.commands += 1
        # Independent rigid-transform classification checks plus malformed data.
        for opened in (False, True):
            points = [SimpleNamespace(x=0., y=0.) for _ in range(21)]
            for tip, base in ((4, 2), (8, 5), (12, 9), (16, 13), (20, 17)):
                points[base] = SimpleNamespace(x=1., y=0.)
                points[tip] = SimpleNamespace(x=3. if opened else .8, y=0.)
            angle, scale = rng.uniform(-math.pi, math.pi), rng.uniform(.2, 2.)
            dx, dy = rng.uniform(-1., 1.), rng.uniform(-1., 1.)
            c, s = math.cos(angle), math.sin(angle)
            rotated = [SimpleNamespace(x=scale*(c*p.x-s*p.y)+dx,
                                       y=scale*(s*p.x+c*p.y)+dy) for p in points]
            if classify_gesture(rotated) != ('open_palm' if opened else 'fist'):
                raise AssertionError('rigid transform changed fixture classification')
            rotated[rng.randrange(21)].x = rng.choice((float('nan'), float('inf'), True))
            if classify_gesture(rotated) != 'other':
                raise AssertionError('malformed landmark accepted')
            self.geometry += 2
        if self.cases % 50 == 0:
            self.thread_case()
        self.cases += 1

    def thread_case(self):
        entered, release = threading.Event(), threading.Event()
        state = SimpleNamespace(connected=True, armed=False)
        interrupted = self.rng.choice(('set_mode', 'arm', 'takeoff'))
        safety = self.rng.choice(('hold', 'land', 'emergency'))
        calls, result = [], []
        def service(operation, value):
            calls.append((operation, value))
            if operation == 'arm':
                state.armed = True
            if operation == interrupted:
                entered.set()
                if not release.wait(2.):
                    raise RuntimeError('thread test release timed out')
            return True
        logic = FlightController(service, lambda: state)
        worker = threading.Thread(target=lambda: result.append(logic.handle('open_palm')),
                                  daemon=True)
        worker.start()
        try:
            if not entered.wait(2.):
                raise AssertionError('thread test did not reach requested boundary')
            # Release blocking applies only to the takeoff worker, not safety's
            # LOITER set_mode callback at the same operation name.
            if interrupted == 'set_mode' and safety == 'hold':
                safety = 'land'
            logic.handle(safety)
        finally:
            release.set()
            worker.join(2.)
        if worker.is_alive() or not result:
            raise AssertionError('thread campaign leaked a worker')
        boundary = next(i for i, pair in enumerate(calls) if pair[0] == interrupted)
        if any(op in ('arm', 'takeoff') or (op, value) == ('set_mode', 'GUIDED')
               for op, value in calls[boundary+1:]):
            raise AssertionError('takeoff advanced after boundary safety interruption')
        self.thread_trials += 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--seed', type=int, default=20261109)
    parser.add_argument('--cases', type=int, default=1000)
    parser.add_argument('--seconds', type=float)
    args = parser.parse_args(argv)
    if (not 1 <= args.cases <= 1000000 or args.seconds is not None and
            (not math.isfinite(args.seconds) or not 1 <= args.seconds <= 14400)):
        parser.error('cases 1..1000000; optional seconds 1..14400')
    initial = manifest()
    campaign = Campaign(args.seed)
    started = last = time.monotonic()
    print(json.dumps({'event': 'start', 'seed': args.seed, 'sources': initial,
                      'scope': 'offline; no ROS, camera, FC or motor activity'}), flush=True)
    while (time.monotonic() - started < args.seconds if args.seconds is not None
           else campaign.cases < args.cases):
        campaign.case()
        now = time.monotonic()
        if now - last >= 60.:
            if manifest() != initial:
                raise RuntimeError('reviewed source changed during campaign; evidence invalidated')
            print(json.dumps({'event': 'progress', 'elapsed_sec': round(now-started, 1),
                              **vars(campaign), 'rng': 'seeded'} , default=lambda _: 'not serialized'),
                  flush=True)
            last = now
    if manifest() != initial:
        raise RuntimeError('reviewed source changed during campaign; evidence invalidated')
    print(json.dumps({'event': 'passed', 'elapsed_sec': round(time.monotonic()-started, 1),
                      'cases': campaign.cases, 'commands': campaign.commands,
                      'geometry': campaign.geometry, 'thread_trials': campaign.thread_trials}), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
