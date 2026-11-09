"""Thin ROS adapter: GUIDED -> arm -> takeoff(2m), LOITER hold, emergency land."""
import threading
import time
import re
import rclpy
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, CommandTOL, SetMode
from rclpy.node import Node
from std_msgs.msg import String
from drone_bringup.flight_logic import FlightController
from drone_bringup.state_watchdog import StateWatchdog
from drone_bringup.state_watchdog import _finite
from drone_bringup.command_admission import CommandAdmission
from drone_bringup.service_circuit import ServiceCircuit

SERVICE_WAIT_TIMEOUT_SEC = 5.0
SERVICE_CALL_TIMEOUT_SEC = 5.0


class FlightCmdBridge(Node):
    def __init__(self):
        super().__init__('flight_cmd_bridge')
        self._stopping = threading.Event()
        self._circuit = ServiceCircuit()
        state_age = self.declare_parameter('state_max_age_sec', 2.0).value
        if not _finite(state_age) or not .1 <= state_age <= 10:
            raise ValueError('state_max_age_sec must be in [0.1,10]')
        self._state_watchdog = StateWatchdog(time.monotonic, state_age)
        self._service_wait = self.declare_parameter(
            'service_wait_timeout_sec', SERVICE_WAIT_TIMEOUT_SEC).value
        self._service_timeout = self.declare_parameter(
            'service_call_timeout_sec', SERVICE_CALL_TIMEOUT_SEC).value
        self._transition_timeout = self.declare_parameter(
            'state_transition_timeout_sec', 5.0).value
        for timeout in (self._service_wait, self._service_timeout, self._transition_timeout):
            if not _finite(timeout) or not .1 <= timeout <= 30:
                raise ValueError('service timeouts must be in [0.1,30] seconds')
        altitude = self.declare_parameter('takeoff_altitude_m', 2.0).value
        self._state_sub = self.create_subscription(
            State, '/mavros/state', self._on_state, 10)
        self._gesture_timeout = self.declare_parameter('gesture_watchdog_sec', 3.0).value
        if not _finite(self._gesture_timeout) or not .5 <= self._gesture_timeout <= 10:
            raise ValueError('gesture_watchdog_sec must be in [0.5,10]')
        self._gesture_received = None
        self._gesture_loss_sent = False
        self._heartbeat_session = None
        self._heartbeat_seq = -1
        self._heartbeat_sub = self.create_subscription(
            String, '/gesture_heartbeat', self._on_gesture_heartbeat, 1)
        self._sub = self.create_subscription(
            String, '/flight_cmd', self._on_flight_cmd, 10)
        self._ack_pub = self.create_publisher(String, '/flight_cmd_ack', 10)
        self._clients = {
            'set_mode': self.create_client(SetMode, '/mavros/set_mode'),
            'arm': self.create_client(CommandBool, '/mavros/cmd/arming'),
            'takeoff': self.create_client(CommandTOL, '/mavros/cmd/takeoff'),
            'land': self.create_client(CommandTOL, '/mavros/cmd/land'),
        }
        self._logic = FlightController(self._call, self._state_watchdog.current,
                                       altitude, self._confirm, clock=time.monotonic,
                                       startup_latched=True)
        self._admission = CommandAdmission()
        self._link_was_connected = False
        self._link_loss_sent = False
        self._link_timer = self.create_timer(0.2, self._check_link)

    def _check_link(self):
        if self._stopping.is_set():
            return
        self._check_gesture()
        self._logic.observe_reset_state()
        state = self._state_watchdog.current()
        if state is not None and state.connected is True:
            self._link_was_connected = True
            return
        if self._link_was_connected and not self._link_loss_sent:
            # One bounded best-effort land attempt per process, no actuation loop.
            # A dead transport cannot deliver it; FC failsafes remain essential.
            self._link_loss_sent = True
            self._on_flight_cmd(String(data='emergency'))

    def _on_gesture_heartbeat(self, msg):
        if self._stopping.is_set() or not isinstance(msg.data, str) or len(msg.data) > 128:
            return
        parts = msg.data.split(':')
        if (len(parts) != 4 or parts[0] != 'v1'
                or re.fullmatch('[0-9a-f]{32}', parts[1]) is None
                or re.fullmatch('[0-9]{1,12}', parts[2]) is None):
            return
        try:
            source_time = float(parts[3])
        except ValueError:
            return
        now, sequence = time.monotonic(), int(parts[2])
        session = getattr(self, '_heartbeat_session', None)
        if (not _finite(source_time) or not _finite(now) or source_time < 0
                or not 0 <= now - source_time <= .5
                or session is not None and session != parts[1]
                or sequence <= getattr(self, '_heartbeat_seq', -1)):
            return
        self._heartbeat_session, self._heartbeat_seq = parts[1], sequence
        self._gesture_received = now

    def _check_gesture(self):
        received = getattr(self, '_gesture_received', None)
        if received is None or getattr(self, '_gesture_loss_sent', False):
            return
        now = time.monotonic()
        if not _finite(now) or now < received or now - received >= self._gesture_timeout:
            self._gesture_loss_sent = True
            self._on_flight_cmd(String(data='emergency'))

    def _on_state(self, msg):
        self._state_watchdog.receive(msg)

    def _on_flight_cmd(self, msg):
        if self._stopping.is_set():
            return
        command = msg.data
        if command in ('land', 'fist', 'emergency'):
            self._logic.latch_landing()
        if command in ('hold', 'land', 'fist', 'emergency'):
            self._logic.invalidate_takeoff()
        if command not in ('open_palm', 'hold', 'land', 'fist', 'emergency'):
            self._handle(command)
            return
        lease = self._admission.acquire(command)
        if lease is None:
            self._ack_pub.publish(String(data=f'{command}:FAIL:busy; command not queued'))
            return
        ticket = self._logic.takeoff_ticket()
        try:
            threading.Thread(target=self._run_admitted,
                             args=(command, lease, ticket), daemon=True).start()
        except Exception:
            self._admission.release(lease)
            raise

    def _run_admitted(self, command, lease, ticket):
        try:
            self._handle(command, ticket)
        finally:
            self._admission.release(lease)

    def _handle(self, command, ticket=None):
        try:
            if ticket is None:
                ok, detail = self._logic.handle(command)
            else:
                ok, detail = self._logic.handle(command, ticket=ticket)
        except Exception as exc:
            ok, detail = False, str(exc)
        if ok and command == 'operator_reset':
            # Resetting the landing latch must re-enable supervision for the next
            # session; a stale heartbeat immediately relatches rather than renews.
            self._gesture_loss_sent = False
            self._link_loss_sent = False
            self._heartbeat_session = None
            self._heartbeat_seq = -1
        if not self._stopping.is_set():
            self._ack_pub.publish(String(
                data=f'{command}:{"OK" if ok else "FAIL"}:{detail}'))

    def _call(self, operation, value):
        circuit = getattr(self, '_circuit', None)
        if circuit is None:
            return self._call_once(operation, value)
        key = (operation, value if operation == 'set_mode' else None)
        return circuit.run(key, lambda: self._call_once(operation, value))

    def _call_once(self, operation, value):
        if self._stopping.is_set():
            return False
        if operation == 'set_mode':
            request = SetMode.Request(custom_mode=value)
        elif operation == 'arm':
            request = CommandBool.Request(value=value)
        else:
            request = CommandTOL.Request()
            if operation == 'takeoff':
                request.altitude = value
        client = self._clients[operation]
        if not client.wait_for_service(timeout_sec=self._service_wait):
            return False
        if self._stopping.is_set():
            return False
        if operation == 'set_mode' and value == 'LOITER' and not self._logic.hold_permitted():
            return False
        if (operation in ('arm', 'takeoff') or operation == 'set_mode' and value == 'GUIDED'):
            if not self._logic.takeoff_permitted():
                return False
        if operation in ('arm', 'takeoff'):
            state = self._state_watchdog.current()
            if state is None or state.connected is not True or state.mode != 'GUIDED':
                return False
            if operation == 'takeoff' and state.armed is not True:
                return False
        if (operation in ('arm', 'takeoff') or operation == 'set_mode' and value == 'GUIDED'):
            if not self._logic.takeoff_permitted():
                return False
        future = client.call_async(request)
        deadline = time.monotonic() + self._service_timeout
        while not future.done():
            if self._stopping.is_set() or time.monotonic() >= deadline:
                return False
            time.sleep(0.02)
        if future.exception() is not None:
            return False
        response = future.result()
        return bool(response and (response.mode_sent if operation == 'set_mode'
                                  else response.success))

    def _confirm(self, operation, value):
        deadline = time.monotonic() + self._transition_timeout
        while not self._stopping.is_set() and time.monotonic() < deadline:
            if not self._logic.takeoff_permitted():
                return False
            state = self._state_watchdog.current()
            if state is not None and state.connected:
                if operation == 'set_mode' and state.mode == value:
                    return True
                if operation == 'arm' and state.armed is value:
                    return True
            time.sleep(0.02)
        return False

    def destroy_node(self):
        self._stopping.set()
        self._logic.invalidate_takeoff()
        return super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = FlightCmdBridge()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        try:
            if node is not None:
                node.destroy_node()
        finally:
            rclpy.shutdown()
