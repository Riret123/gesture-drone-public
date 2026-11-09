import json
from pathlib import Path
import uuid
import unittest
from unittest.mock import patch
from gesture_control.pose_features import PoseProfile
from gesture_control.pose_profile_io import load_profile, save_profile


class ProfilePersistenceTests(unittest.TestCase):
    def setUp(self):
        directory = Path(__file__).resolve().parents[1] / ('profile-test-' + uuid.uuid4().hex)
        directory.mkdir()
        def cleanup():
            for item in directory.iterdir():
                item.unlink()
            directory.rmdir()
        self.addCleanup(cleanup)
        self.path = directory / 'profile.json'
        self.identity = dict(camera_id='fixture-camera-v1', model_id='fixture-model-v1')
        save_profile(self.path, PoseProfile(), **self.identity)

    def test_round_trip(self):
        self.assertEqual(load_profile(self.path, **self.identity), PoseProfile())

    def test_identity_and_schema_fail_closed(self):
        baseline = self.path.read_text()
        for field, value in (('version', True), ('version', 2), ('camera_id', 'other'),
                             ('model_id', 'other'), ('unknown', 1), ('profile', [])):
            with self.subTest(field=field, value=value):
                data = json.loads(baseline)
                data[field] = value
                self.path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    load_profile(self.path, **self.identity)

    def test_duplicates_oversize_nonfinite_and_bad_angles(self):
        baseline = self.path.read_text()
        invalid = ['{' + baseline[1:-2] + ',"version":1}', ' ' * 8193,
                   baseline.replace('110.0', 'NaN'),
                   baseline.replace('110.0', 'true'),
                   baseline.replace('160.0', '90.0')]
        for payload in invalid:
            self.path.write_text(payload)
            with self.assertRaises(ValueError):
                load_profile(self.path, **self.identity)

    def test_failed_replace_preserves_old_profile_and_removes_temp(self):
        baseline = self.path.read_bytes()
        with patch('gesture_control.pose_profile_io.os.replace', side_effect=OSError('disk')):
            with self.assertRaises(OSError):
                save_profile(self.path, PoseProfile(100., 170., .6), **self.identity)
        self.assertEqual(self.path.read_bytes(), baseline)
        self.assertEqual(list(self.path.parent.iterdir()), [self.path])

    def test_deployment_profile_cannot_disable_margin_gate(self):
        for profile in (PoseProfile(min_confidence=.49), PoseProfile(155., 160., .5)):
            with self.assertRaises(ValueError):
                save_profile(self.path, profile, **self.identity)

    def test_exclusive_name_collision_never_deletes_existing_file(self):
        collision = self.path.parent / '.profile-collision.tmp'
        collision.write_text('preserve-existing-data')
        with patch('gesture_control.pose_profile_io.uuid.uuid4') as identifier:
            identifier.return_value.hex = 'collision'
            with self.assertRaises(FileExistsError):
                save_profile(self.path, PoseProfile(), **self.identity)
        self.assertEqual(collision.read_text(), 'preserve-existing-data')
