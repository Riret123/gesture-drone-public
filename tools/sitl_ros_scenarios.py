"""Plan by default; explicit isolated-SITL execution imports ROS lazily.

Never run against physical aircraft. Endpoint and isolation flags are operator
attestations, not physical hardware detection. Linux/ROS execution is unverified.
"""
import argparse
from collections import deque
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/drone_bringup'))
from drone_bringup.sitl_scenarios import SCENARIOS, plan, run_scenario
from drone_bringup.sitl_observations import ObservationLimits, ScenarioObservations


class LiveTransport:
    def __init__(self, rc_mode='LAND'):
        import rclpy
        from geometry_msgs.msg import PoseStamped
        from mavros_msgs.msg import State, ExtendedState
        from mavros_msgs.srv import ParamSetV2
        from rcl_interfaces.msg import ParameterValue
        from rcl_interfaces.srv import GetParameters
        from rclpy.qos import qos_profile_sensor_data
        from std_msgs.msg import String, Float64
        self.ros, self.String = rclpy, String
        self.GetParameters, self.ParamSetV2 = GetParameters, ParamSetV2
        self.ParameterValue = ParameterValue
        self.node = rclpy.create_node('isolated_sitl_scenario')
        self.observations = ScenarioObservations(ObservationLimits(rc_mode=rc_mode))
        self._acks = deque(maxlen=64)
        self._fault_attempted = False
        self.pub = self.node.create_publisher(String, '/flight_cmd', 10)
        qos = qos_profile_sensor_data
        self.subscriptions = [
            self.node.create_subscription(State, '/mavros/state', self._state, qos),
            self.node.create_subscription(ExtendedState, '/mavros/extended_state',
                lambda m: self.observations.update_landed(m.landed_state, time.monotonic()), qos),
            self.node.create_subscription(Float64, '/mavros/global_position/rel_alt',
                lambda m: self.observations.update_altitude(m.data, time.monotonic()), qos),
            self.node.create_subscription(PoseStamped, '/mavros/local_position/pose',
                self._position, qos),
            self.node.create_subscription(String, '/flight_cmd_ack',
                lambda m: self._acks.append((time.monotonic(), m.data)), 10)]
        self._get_client = self.node.create_client(GetParameters, '/mavros/param/get_parameters')
        self._set_client = self.node.create_client(ParamSetV2, '/mavros/param/set')

    def _state(self, message):
        self.observations.update_state(message.connected, message.armed,
                                       message.mode, time.monotonic())

    def _position(self, message):
        p = message.pose.position
        self.observations.update_position((p.x, p.y, p.z), time.monotonic())

    def _request(self, client, request):
        if not client.wait_for_service(timeout_sec=5.):
            return None
        future = client.call_async(request)
        self.ros.spin_until_future_complete(self.node, future, timeout_sec=5.)
        if not future.done() or future.exception() is not None:
            return None
        return future.result()

    def verify_simulator_parameter(self):
        # Cached SIM_* presence is an extra refusal gate, not proof of hardware isolation.
        result = self._request(self._get_client,
            self.GetParameters.Request(names=['SIM_RC_FAIL']))
        if result is None or len(result.values) != 1:
            return False
        value = result.values[0]
        return (value.type == 2 and value.integer_value == 0
                or value.type == 3 and value.double_value == 0.)

    def command(self, command):
        # Exactly one command subscriber and publisher; no camera/keyboard source.
        deadline = time.monotonic() + 5.
        while self.pub.get_subscription_count() != 1:
            if time.monotonic() >= deadline:
                return False
            self.ros.spin_once(self.node, timeout_sec=.1)
        if self.node.count_publishers('/flight_cmd') != 1:
            return False
        self._acks.clear()
        sent = time.monotonic()
        self.pub.publish(self.String(data=command))
        deadline = sent + 45.
        while time.monotonic() < deadline:
            self.ros.spin_once(self.node, timeout_sec=.1)
            while self._acks:
                received, text = self._acks.popleft()
                parts = text.split(':', 2)
                if received >= sent and len(parts) == 3 and parts[0] == command:
                    return parts[1] == 'OK'
        return False

    def expect(self, condition, timeout):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.ros.spin_once(self.node, timeout_sec=.1)
            if self.observations.ready(condition, time.monotonic()):
                return True
        return False

    def _set_sim_rc(self, value):
        if type(value) is not int or value not in (0, 1):
            raise ValueError('only simulated RC loss/restore is supported')
        response = self._request(self._set_client, self.ParamSetV2.Request(
            force_set=False, param_id='SIM_RC_FAIL',
            value=self.ParameterValue(type=2, integer_value=value)))
        if response is None or response.success is not True:
            return False
        observed = response.value
        return (observed.type == 2 and observed.integer_value == value
                or observed.type == 3 and observed.double_value == value)

    def fault(self, name):
        if name != 'rc_loss':
            raise ValueError('unknown simulator fault')
        self._fault_attempted = True  # Timeout is uncertain: restoration still required.
        if not self._set_sim_rc(1):
            return False
        self.observations.mark_rc_fault(time.monotonic())
        return True

    def restore_fault(self):
        if not self._fault_attempted:
            return True
        return self._set_sim_rc(0)


def run_live(args):
    import rclpy
    rclpy.init(args=[])
    transport = None
    ok, detail = False, 'not started'
    try:
        transport = LiveTransport(args.rc_mode)
        if not transport.verify_simulator_parameter():
            detail = 'SIM_RC_FAIL must exist and be zero; no flight commands sent'
        else:
            ok, detail = run_scenario(args.scenario, transport)
    except (Exception, KeyboardInterrupt):
        ok, detail = False, 'scenario interrupted or adapter failed; manual SITL recovery required'
    finally:
        try:
            if transport is not None:
                try:
                    if not transport.restore_fault():
                        ok, detail = False, 'SIM_RC_FAIL restoration failed; restore manually in SITL'
                except (Exception, KeyboardInterrupt):
                    ok, detail = False, 'SIM_RC_FAIL restoration uncertain; restore manually in SITL'
                finally:
                    transport.node.destroy_node()
        finally:
            rclpy.shutdown()
    print(json.dumps({'passed': ok, 'detail': detail, 'execution': 'live SITL requested'}))
    return 0 if ok else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenario', choices=SCENARIOS)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--sitl-isolated', action='store_true')
    parser.add_argument('--fcu-url')
    parser.add_argument('--allow-rc-fault', action='store_true')
    parser.add_argument('--rc-mode', choices=('LAND', 'RTL', 'SMART_RTL'), default='LAND')
    args = parser.parse_args(argv)
    if not args.execute:
        print(json.dumps({'steps': plan(args.scenario), 'execution': 'none; plan only'}))
        return 0
    if not args.sitl_isolated or args.fcu_url != 'udp://:14550@':
        parser.error('execution requires physical isolation and attested --fcu-url udp://:14550@')
    if args.scenario == 'rc-loss' and not args.allow_rc_fault:
        parser.error('rc-loss also requires --allow-rc-fault; changes SIM_RC_FAIL only')
    return run_live(args)


if __name__ == '__main__':
    raise SystemExit(main())
