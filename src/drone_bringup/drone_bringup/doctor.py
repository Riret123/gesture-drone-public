"""Read-only deployment diagnostics. Never publishes or calls FC services."""
from dataclasses import asdict, dataclass
import os
import json
import re
from pathlib import Path
import shutil
from .bounded_probe import run_probe


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


COMMANDS = {
    'time_sync': ('timedatectl', 'show', '-p', 'NTPSynchronized', '--value'),
    'topics': ('ros2', 'topic', 'list'),
    'services': ('ros2', 'service', 'list'),
    'fc_state': ('ros2', 'topic', 'echo', '/mavros/state', '--once'),
}
EXPECTED_TYPES = {
    'state_type': ('topic', '/mavros/state', 'mavros_msgs/msg/State'),
    'command_type': ('topic', '/flight_cmd', 'std_msgs/msg/String'),
    'ack_type': ('topic', '/flight_cmd_ack', 'std_msgs/msg/String'),
    'mode_service_type': ('service', '/mavros/set_mode', 'mavros_msgs/srv/SetMode'),
    'arm_service_type': ('service', '/mavros/cmd/arming', 'mavros_msgs/srv/CommandBool'),
    'takeoff_service_type': ('service', '/mavros/cmd/takeoff', 'mavros_msgs/srv/CommandTOL'),
    'land_service_type': ('service', '/mavros/cmd/land', 'mavros_msgs/srv/CommandTOL'),
}
COMMANDS.update({name: ('ros2', kind, 'type', path)
                 for name, (kind, path, _) in EXPECTED_TYPES.items()})
CAMERA_PROBE = (
    'import cv2; c=cv2.VideoCapture(0); '
    'ok, frame=c.read(); c.release(); '
    'raise SystemExit(0 if ok and frame is not None else 2)')


def bounded_run(argv):
    """A separate probe process bounds native camera hangs without restarting flight."""
    return run_probe(argv)


def _state_string(value, maximum):
    if value.startswith('"'):
        try:
            value = json.loads(value)
        except ValueError:
            return False
    elif value.startswith("'"):
        if not value.endswith("'") or len(value) < 2:
            return False
        value = value[1:-1].replace("''", "'")
    elif not value:
        return False
    return (isinstance(value, str) and len(value) <= maximum
            and re.fullmatch(r'[A-Za-z0-9_./+\-]*', value) is not None)


def connected_disarmed(output):
    """Accept one unambiguous state, never merge contradictory observations."""
    if not isinstance(output, str) or len(output) > 16384:
        return False
    lines = [line.rstrip() for line in output.splitlines() if line.strip()]
    if lines and lines[-1] == '---':
        lines.pop()
    fields, nested = {}, set()
    parent = header_child = None
    for line in lines:
        if '\t' in line or any(ord(char) < 32 for char in line):
            return False
        indent = len(line) - len(line.lstrip(' '))
        key, separator, value = line.strip().partition(':')
        value = value.strip()
        if not separator:
            return False
        if indent:
            if parent != 'header':
                return False
            if indent == 2 and key in ('stamp', 'frame_id'):
                token = key
                header_child = key
                if key == 'stamp' and value:
                    return False
                if key == 'frame_id' and not _state_string(value, 256):
                    return False
            elif indent == 4 and key in ('sec', 'nanosec') and header_child == 'stamp':
                token = 'stamp.' + key
                if not value.isascii() or not value.isdecimal():
                    return False
                if len(value) > 12 or key == 'nanosec' and int(value) >= 1_000_000_000:
                    return False
                if key == 'sec' and int(value) > 2_147_483_647:
                    return False
            else:
                return False
            if token in nested:
                return False
            nested.add(token)
            continue
        if key in fields or key not in (
                'header', 'connected', 'armed', 'guided', 'manual_input', 'mode', 'system_status'):
            return False
        if key in ('connected', 'armed', 'guided', 'manual_input') and value not in ('true', 'false'):
            return False
        if key == 'header' and value:
            return False
        if key == 'system_status' and (not value.isascii() or not value.isdecimal()
                                       or len(value) > 3 or int(value) > 255):
            return False
        if key == 'mode' and not _state_string(value, 96):
            return False
        fields[key], parent = value, key
    return fields.get('connected') == 'true' and fields.get('armed') == 'false'


def diagnose(workspace, *, probe_camera=False, run=bounded_run,
             environ=None, disk_usage=shutil.disk_usage, devices=None):
    workspace = Path(workspace)
    environ = os.environ if environ is None else environ
    results = []
    ros_ready = environ.get('ROS_DISTRO') == 'jazzy' and bool(environ.get('AMENT_PREFIX_PATH'))
    results.append(Check('ros_environment', 'pass' if ros_ready else 'fail',
                         'Jazzy and overlay required; source ROS then install/setup.bash'))
    try:
        free = disk_usage(workspace).free
        results.append(Check('disk', 'pass' if free >= 2 * 1024**3 else 'fail',
                             'At least 2 GiB free required for this diagnostic gate'))
    except OSError:
        results.append(Check('disk', 'fail', 'Workspace unavailable'))
    if devices is None:
        devices = [*Path('/dev').glob('ttyUSB*'), *Path('/dev').glob('ttyACM*'),
                   *Path('/dev').glob('ttyS*'), *Path('/dev').glob('video*')]
    names = [Path(path).name for path in devices]
    results.append(Check('serial', 'pass' if any(name.startswith(('ttyUSB', 'ttyACM', 'ttyS'))
                                               for name in names) else 'warn',
                         'Presence only; verify selected UART, pinmux, baud and permissions manually'))
    results.append(Check('camera_device', 'pass' if 'video0' in names else 'warn',
                         'Device presence does not establish image quality or latency'))
    status, output = run(COMMANDS['time_sync'])
    results.append(Check('time_sync', 'pass' if status == 0 and output.strip() == 'yes' else 'warn',
                         'Require synchronized system clock; control freshness uses monotonic time'))
    if ros_ready:
        status, output = run(COMMANDS['topics'])
        required = {'/mavros/state', '/flight_cmd', '/flight_cmd_ack'}
        results.append(Check('topics', 'pass' if status == 0 and required <= set(output.split()) else 'fail',
                             'Required topic names must exist; names alone do not prove publisher health'))
        status, output = run(COMMANDS['services'])
        required = {'/mavros/set_mode', '/mavros/cmd/arming', '/mavros/cmd/takeoff', '/mavros/cmd/land'}
        results.append(Check('services', 'pass' if status == 0 and required <= set(output.split()) else 'fail',
                             'Service discovery only; no service invoked'))
        status, output = run(COMMANDS['fc_state'])
        results.append(Check('fc_state', 'pass' if status == 0 and connected_disarmed(output) else 'fail',
                             'Require a returned connected/disarmed observation; not hardware identity'))
        for name, (_, _, expected) in EXPECTED_TYPES.items():
            status, output = run(COMMANDS[name])
            results.append(Check(name, 'pass' if status == 0 and output.strip() == expected else 'fail',
                                 'Require the exact installed ROS interface; not publisher authentication'))
    else:
        results.append(Check('ros_probes', 'fail', 'Skipped: ROS environment not sourced'))
    if probe_camera:
        import sys
        status, _ = run((sys.executable, '-c', CAMERA_PROBE))
        results.append(Check('camera_capture', 'pass' if status == 0 else 'fail',
                             'Exclusive camera probe; stop gesture/video owners first; no image saved'))
    return [asdict(result) for result in results]
