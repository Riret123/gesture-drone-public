"""Strict versioned local-ENU mission files for offline simulation only.

Coordinates are metres east, north, up relative to a caller-defined home.
Parsing a mission never authorizes flight and never imports ROS or opens files.
"""
from dataclasses import dataclass
import json
import math
import re

from .validation import finite

MAX_BYTES = 65536
MAX_WAYPOINTS = 256
NAME = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,31}\Z')


def number(value, name, low, high):
    """Reject bools, NaN, infinity, overflow, and out-of-domain numbers."""
    if not finite(value) or not low <= value <= high:
        raise ValueError(f'{name}: expected finite number in [{low}, {high}]')
    return float(value)


def keys(value, required, optional=()):
    if type(value) is not dict or set(value) - set(required) - set(optional):
        raise ValueError('object has unknown fields or is not an object')
    if set(required) - set(value):
        raise ValueError('object missing required fields')


@dataclass(frozen=True)
class Waypoint:
    name: str
    east: float
    north: float
    up: float
    dwell: float = 0.0

    def __post_init__(self):
        if type(self.name) is not str or NAME.fullmatch(self.name) is None:
            raise ValueError('invalid waypoint name')
        number(self.east, 'east', -10000, 10000)
        number(self.north, 'north', -10000, 10000)
        number(self.up, 'up', 0, 1000)
        number(self.dwell, 'dwell', 0, 3600)

    @property
    def position(self):
        return (self.east, self.north, self.up)


@dataclass(frozen=True)
class Mission:
    waypoints: tuple
    speed: float = 0.2
    radius: float = 20.0
    ceiling: float = 5.0
    version: int = 1
    frame: str = 'local_enu'

    def __post_init__(self):
        if type(self.version) is not int or self.version != 1:
            raise ValueError('only integer mission version 1 is supported')
        if self.frame != 'local_enu' or type(self.frame) is not str:
            raise ValueError('frame must be local_enu')
        number(self.speed, 'speed', 0.01, 2.0)
        number(self.radius, 'radius', 0.1, 10000)
        number(self.ceiling, 'ceiling', 0.1, 1000)
        if type(self.waypoints) is not tuple or not 1 <= len(self.waypoints) <= MAX_WAYPOINTS:
            raise ValueError('waypoints must be a bounded nonempty tuple')
        if any(type(w) is not Waypoint for w in self.waypoints):
            raise ValueError('waypoints must be validated Waypoint objects')
        if len({w.name for w in self.waypoints}) != len(self.waypoints):
            raise ValueError('waypoint names must be unique')
        for w in self.waypoints:
            if math.hypot(w.east, w.north) >= self.radius or w.up >= self.ceiling:
                raise ValueError('waypoint touches or exceeds offline fence')

    @classmethod
    def from_dict(cls, value):
        keys(value, ('version', 'frame', 'waypoints'), ('speed', 'radius', 'ceiling'))
        rows = value['waypoints']
        if type(rows) is not list or not 1 <= len(rows) <= MAX_WAYPOINTS:
            raise ValueError('waypoints must be a bounded nonempty JSON array')
        points = []
        for row in rows:
            keys(row, ('name', 'east', 'north', 'up'), ('dwell',))
            points.append(Waypoint(**row))
        return cls(tuple(points), value.get('speed', 0.2), value.get('radius', 20.0),
                   value.get('ceiling', 5.0), value['version'], value['frame'])

    @classmethod
    def from_json(cls, source):
        if type(source) is not str or len(source) > MAX_BYTES:
            raise ValueError('mission must be bounded JSON text')
        try:
            if len(source.encode('utf-8')) > MAX_BYTES:
                raise ValueError('mission exceeds byte limit')
            def unique_pairs(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError('duplicate JSON field')
                    result[key] = value
                return result
            def reject_constant(value):
                raise ValueError('nonstandard JSON number')
            obj = json.loads(source, object_pairs_hook=unique_pairs,
                             parse_constant=reject_constant)
            return cls.from_dict(obj)
        except (UnicodeError, RecursionError, json.JSONDecodeError) as exc:
            raise ValueError('invalid mission JSON') from exc

    def to_dict(self):
        return {'version': self.version, 'frame': self.frame, 'speed': self.speed,
                'radius': self.radius, 'ceiling': self.ceiling,
                'waypoints': [{'name': w.name, 'east': w.east, 'north': w.north,
                               'up': w.up, 'dwell': w.dwell} for w in self.waypoints]}

    def to_json(self):
        return json.dumps(self.to_dict(), allow_nan=False, sort_keys=True,
                          separators=(',', ':'))
