#!/usr/bin/env python3
"""Legacy live bridge checks for explicitly isolated ArduPilot SITL only.

Checks service ACKs, armed observations, duplicate skips and landing inhibition.
It does NOT measure altitude or prove touchdown. Prefer the observed-outcome
runner in tools/sitl_ros_scenarios.py. Requires manual startup dwell/operator
reset first, no camera publisher, physical FC isolation and an explicit UDP
endpoint attestation. Flags do not detect hardware. No automatic flight retry.
"""

from __future__ import annotations

import argparse
import sys
import time


SUBSCRIBER_WAIT_TIMEOUT_SEC = 5.0
ACK_WAIT_TIMEOUT_SEC = 45.0  # Three service waits/responses plus two state confirmations.
STATE_WAIT_TIMEOUT_SEC = 10.0
LANDING_WAIT_TIMEOUT_SEC = 60.0  # SITL speedup=1, реальная посадка с 2м не мгновенная

failures = []


def check(label, condition, detail=''):
    status = 'OK' if condition else 'FAIL'
    print(f'[{status}] {label}' + (f' ({detail})' if detail else ''))
    if not condition:
        failures.append(label)


class BridgeTester:

    def __init__(self):
        self.node = rclpy.create_node('flight_cmd_bridge_test')
        self.pub = self.node.create_publisher(String, '/flight_cmd', 10)
        self._acks = []
        self._state = None
        self._state_received = None
        self.node.create_subscription(String, '/flight_cmd_ack', self._on_ack, 10)
        self.node.create_subscription(State, '/mavros/state', self._on_state, 10)

    def _on_ack(self, msg: String):
        self._acks.append(msg.data)
        del self._acks[:-64]

    def _on_state(self, msg: State):
        self._state = msg
        self._state_received = time.monotonic()

    def spin(self, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            rclpy.spin_once(self.node, timeout_sec=0.1)

    def wait_for_bridge_subscriber(self, timeout_sec):
        deadline = time.monotonic() + timeout_sec
        while self.pub.get_subscription_count() != 1:
            if time.monotonic() > deadline:
                return False
            rclpy.spin_once(self.node, timeout_sec=0.1)
        return True

    def publish_and_wait_ack(self, gesture, timeout_sec=ACK_WAIT_TIMEOUT_SEC):
        self._acks.clear()
        msg = String()
        msg.data = gesture
        self.pub.publish(msg)
        deadline = time.monotonic() + timeout_sec
        while time.monotonic() <= deadline:
            for ack in self._acks:
                try:
                    command, _, _ = parse_ack(ack)
                except ValueError:
                    continue
                if command == gesture:
                    return ack
            rclpy.spin_once(self.node, timeout_sec=0.1)
        return None

    def wait_for_armed(self, expected_armed, timeout_sec):
        deadline = time.monotonic() + timeout_sec
        while True:
            if (self._state is not None and self._state.connected
                    and self._state_received is not None
                    and 0 <= time.monotonic() - self._state_received < 2.0
                    and self._state.armed == expected_armed):
                return True
            if time.monotonic() > deadline:
                return False
            rclpy.spin_once(self.node, timeout_sec=0.2)

    def shutdown(self):
        self.node.destroy_node()


def parse_ack(ack_text):
    if not isinstance(ack_text, str):
        raise ValueError('ack must be text')
    parts = ack_text.split(':', 2)
    if (len(parts) != 3 or parts[0] not in
            ('open_palm', 'fist', 'other', 'hold', 'land', 'emergency', 'operator_reset')
            or parts[1] not in ('OK', 'FAIL')):
        raise ValueError('invalid acknowledgement')
    gesture, status, detail = parts
    return gesture, status, detail


def _require_ack(tester, command, required_detail=None, expected_status='OK'):
    ack = tester.publish_and_wait_ack(command)
    if ack is None:
        raise RuntimeError(f'{command}: missing ACK; manual SITL recovery required')
    matched, status, detail = parse_ack(ack)
    if matched != command or status != expected_status:
        raise RuntimeError(f'{command}: unexpected ACK; manual SITL recovery required')
    if required_detail is not None and required_detail not in detail:
        raise RuntimeError(f'{command}: expected service detail missing; stop')
    return detail


def run_legacy_checks(tester):
    if not tester.wait_for_bridge_subscriber(SUBSCRIBER_WAIT_TIMEOUT_SEC):
        raise RuntimeError('one bridge subscriber required; no commands sent')
    tester.spin(2.0)
    if tester.node.count_publishers('/mavros/state') != 1:
        raise RuntimeError('one MAVROS state publisher required; no commands sent')
    if tester.node.count_publishers('/flight_cmd') != 1:
        raise RuntimeError('one command publisher required; stop other command nodes')
    if not tester.wait_for_armed(False, STATE_WAIT_TIMEOUT_SEC):
        raise RuntimeError('fresh connected/disarmed initial state required; nothing sent')
    _require_ack(tester, 'open_palm', 'takeoff(2.0m)=OK')
    if not tester.wait_for_armed(True, STATE_WAIT_TIMEOUT_SEC):
        raise RuntimeError('armed state not observed; manual SITL recovery required')
    # This is an explicit simulator duplicate-command test, never a retry after
    # uncertain acceptance. First ACK and armed observation must already pass.
    _require_ack(tester, 'open_palm', 'arm=SKIP')
    _require_ack(tester, 'fist', 'land=OK')
    if not tester.wait_for_armed(False, LANDING_WAIT_TIMEOUT_SEC):
        raise RuntimeError('disarm not observed; manual SITL recovery required')
    _require_ack(tester, 'fist', 'land=SKIP')
    _require_ack(tester, 'open_palm', 'landing latch', expected_status='FAIL')
    _require_ack(tester, 'other')
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sitl-isolated', action='store_true')
    parser.add_argument('--fcu-url')
    args = parser.parse_args(argv)
    if not args.sitl_isolated or args.fcu_url != 'udp://:14550@':
        parser.error('physical isolation and --fcu-url udp://:14550@ required')
    global rclpy, State, String
    import rclpy
    from mavros_msgs.msg import State
    from std_msgs.msg import String
    tester = None
    rclpy.init(args=[])
    try:
        tester = BridgeTester()
        run_legacy_checks(tester)
        print('PASS: service/armed/skip/latch checks; altitude and touchdown unmeasured')
        return 0
    except (Exception, KeyboardInterrupt):
        print('FAIL: legacy SITL check stopped; inspect state and recover simulator manually')
        return 1
    finally:
        try:
            if tester is not None:
                tester.shutdown()
        finally:
            rclpy.shutdown()


if __name__ == '__main__':
    raise SystemExit(main())
