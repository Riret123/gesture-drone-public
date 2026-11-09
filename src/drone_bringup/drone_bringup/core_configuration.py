"""Fail-closed schema for the deliberately small numeric core ROS YAML file.

This is a restricted YAML subset, not a general YAML parser. No tags, aliases,
flow collections, duplicate keys or implicit booleans are supported.
"""
import json
import re
from .state_watchdog import _finite


# name: (strict integer, lower, upper, lower inclusive)
SCHEMA = {
    'gesture_node': {
        'debounce_frames': (True, 1, 120, True),
        'hold_after_sec': (False, .1, 10, True),
        'land_after_sec': (False, .2, 30, True),
        'curl_ratio': (False, 1, 3, False),
        'camera_index': (True, 0, 32, True),
        'camera_width': (True, 160, 1920, True),
        'camera_height': (True, 120, 1080, True),
        'camera_fps': (False, 5, 60, True),
        'model_complexity': (True, 0, 1, True),
        'detection_confidence': (False, 0, 1, False),
        'tracking_confidence': (False, 0, 1, False),
        'frame_budget_ms': (False, 20, 500, True),
    },
    'flight_cmd_bridge': {
        'state_max_age_sec': (False, .1, 10, True),
        'gesture_watchdog_sec': (False, .5, 10, True),
        'service_wait_timeout_sec': (False, .1, 30, True),
        'service_call_timeout_sec': (False, .1, 30, True),
        'state_transition_timeout_sec': (False, .1, 30, True),
        'takeoff_altitude_m': (False, 0, 2, False),
    },
}


def validate_core(data):
    if not isinstance(data, dict) or set(data) != set(SCHEMA):
        raise ValueError('require exactly gesture_node and flight_cmd_bridge')
    for node, fields in SCHEMA.items():
        section = data[node]
        if not isinstance(section, dict) or set(section) != {'ros__parameters'}:
            raise ValueError(f'{node}: require only ros__parameters')
        params = section['ros__parameters']
        expected = set(fields) | ({'pose_profile_path'} if node == 'gesture_node' else set())
        if not isinstance(params, dict) or set(params) != expected:
            raise ValueError(f'{node}: missing or unknown parameter')
        if node == 'gesture_node':
            path = params['pose_profile_path']
            if (not isinstance(path, str) or len(path) > 1024
                    or any(c in path for c in '\x00\r\n')):
                raise ValueError('pose_profile_path must be a bounded local path')
        for key, (integer, low, high, inclusive) in fields.items():
            value = params[key]
            if (not _finite(value) or integer and type(value) is not int
                    or value > high or (value < low if inclusive else value <= low)):
                raise ValueError(f'{node}.{key}: outside reviewed bounds')
    gesture = data['gesture_node']['ros__parameters']
    if gesture['hold_after_sec'] >= gesture['land_after_sec']:
        raise ValueError('hold must precede landing')
    return data


def parse_core_yaml(text):
    if not isinstance(text, str) or len(text) > 16384:
        raise ValueError('core YAML must be text <=16384 characters')
    data, node, params = {}, None, None
    for number, raw in enumerate(text.splitlines(), 1):
        quoted, escaped, cut = False, False, len(raw)
        for index, char in enumerate(raw):
            if escaped:
                escaped = False
            elif char == '\\' and quoted:
                escaped = True
            elif char == '"':
                quoted = not quoted
            elif char == '#' and not quoted:
                cut = index
                break
        line = raw[:cut].rstrip()
        if not line.strip():
            continue
        if '\t' in line:
            raise ValueError(f'line {number}: tabs unsupported')
        if re.fullmatch(r'[a-z_]+:', line):
            node = line[:-1]
            if node in data:
                raise ValueError('duplicate node')
            data[node] = {}
            params = None
        elif line == '  ros__parameters:' and node is not None:
            if 'ros__parameters' in data[node]:
                raise ValueError('duplicate parameter section')
            params = data[node]['ros__parameters'] = {}
        else:
            match = re.fullmatch(r'    ([a-z_]+): (-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?|"[^"\\]*(?:\\.[^"\\]*)*")', line)
            if match is None or params is None:
                raise ValueError(f'line {number}: unsupported core YAML syntax')
            key, value = match.groups()
            if key in params:
                raise ValueError('duplicate parameter')
            params[key] = json.loads(value)
    return validate_core(data)
