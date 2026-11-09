"""Adversarial mission parsing tests; no vehicle connections."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

from gesture_control.mission_schema import Mission, Waypoint, MAX_BYTES


def valid():
    return {'version': 1, 'frame': 'local_enu', 'waypoints': [
        {'name': 'start', 'east': 0, 'north': 0, 'up': 1}]}


class MissionSchemaTests(unittest.TestCase):
    def test_roundtrip(self):
        plan = Mission.from_dict(valid())
        self.assertEqual(Mission.from_json(plan.to_json()), plan)

    def test_duplicate_json_fields(self):
        for text in ('{"version":1,"version":1}',
                     '{"waypoints":[{"name":"a","name":"b"}]}'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                Mission.from_json(text)

    def test_unknown_fields(self):
        obj = valid()
        obj['command'] = 'ignored'
        with self.assertRaises(ValueError):
            Mission.from_dict(obj)

    def test_strict_version(self):
        for value in (True, 1.0, '1', 0, 2, None):
            obj = valid()
            obj['version'] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                Mission.from_dict(obj)

    def test_frame_must_be_explicit(self):
        for frame in ('ned', 'wgs84', None, 1):
            obj = valid()
            obj['frame'] = frame
            with self.subTest(frame=frame), self.assertRaises(ValueError):
                Mission.from_dict(obj)

    def test_nonfinite_or_boolean_coordinates(self):
        for value in (True, '0', None, float('nan'), float('inf'), 10 ** 1000):
            for field in ('east', 'north', 'up', 'dwell'):
                obj = valid()
                obj['waypoints'][0][field] = value
                with self.subTest(field=field, value=repr(value)[:30]), self.assertRaises(ValueError):
                    Mission.from_dict(obj)

    def test_fence_boundary_is_excluded(self):
        for east, north, up in ((20, 0, 1), (0, -20, 1), (0, 0, 5), (0, 0, -1)):
            obj = valid()
            obj['waypoints'][0].update(east=east, north=north, up=up)
            with self.subTest(position=(east, north, up)), self.assertRaises(ValueError):
                Mission.from_dict(obj)

    def test_duplicate_waypoint_names(self):
        obj = valid()
        obj['waypoints'] *= 2
        with self.assertRaises(ValueError):
            Mission.from_dict(obj)

    def test_waypoint_name_grammar(self):
        for name in ('', '../a', 'a b', '<script>', 'a' * 33, True):
            with self.subTest(name=name), self.assertRaises(ValueError):
                Waypoint(name, 0, 0, 1)

    def test_count_bounds(self):
        for rows in ([], {}, None, [valid()['waypoints'][0]] * 257):
            obj = valid()
            obj['waypoints'] = rows
            with self.subTest(rows=type(rows)), self.assertRaises(ValueError):
                Mission.from_dict(obj)

    def test_input_limits_and_unicode(self):
        for text in (None, b'{}', ' ' * (MAX_BYTES + 1), '\ud800', '[' * 2000):
            with self.subTest(text=repr(text)[:30]), self.assertRaises(ValueError):
                Mission.from_json(text)

    def test_nonstandard_json_constants(self):
        for constant in ('NaN', 'Infinity', '-Infinity'):
            source = json.dumps(valid()).replace('"east": 0', '"east": ' + constant)
            with self.subTest(constant=constant), self.assertRaises(ValueError):
                Mission.from_json(source)

    def test_direct_constructor_cannot_bypass_validation(self):
        for kwargs in ({'speed': True}, {'waypoints': []}, {'version': True},
                       {'radius': 1}, {'ceiling': 1}):
            args = {'waypoints': (Waypoint('a', 1, 0, 1),)}
            args.update(kwargs)
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Mission(**args)

    def test_snapshot_does_not_share_mutable_rows(self):
        plan = Mission.from_dict(valid())
        exported = plan.to_dict()
        exported['waypoints'][0]['up'] = 999
        self.assertEqual(plan.waypoints[0].up, 1)

    def test_maximum_valid_plan_fits_ingestion_limit(self):
        points = tuple(Waypoint('p' + str(i).zfill(31), 1.1234567890123457,
                                -1.2345678901234567, 3.1234567890123457,
                                3599.1234567890123) for i in range(256))
        plan = Mission(points)
        self.assertLessEqual(len(plan.to_json().encode('utf-8')), MAX_BYTES)
        self.assertEqual(Mission.from_json(plan.to_json()), plan)

    def test_plan_level_numeric_mutations(self):
        for field in ('speed', 'radius', 'ceiling'):
            for bad in (True, None, '1', 0, -1, float('nan'), float('inf'), 10 ** 1000):
                obj = valid()
                obj[field] = bad
                with self.subTest(field=field, bad=repr(bad)[:20]), self.assertRaises(ValueError):
                    Mission.from_dict(obj)

    def test_utf8_limit_is_bytes_not_characters(self):
        with self.assertRaises(ValueError):
            Mission.from_json('é' * (MAX_BYTES // 2 + 1))

    def test_export_keys_exact(self):
        obj = Mission.from_dict(valid()).to_dict()
        self.assertEqual(set(obj), {'version', 'frame', 'waypoints', 'speed', 'radius', 'ceiling'})
        self.assertEqual(set(obj['waypoints'][0]), {'name', 'east', 'north', 'up', 'dwell'})
