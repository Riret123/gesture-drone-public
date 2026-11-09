import base64
import hashlib
import json
import unittest
import zlib
from drone_bringup.firmware_artifact import inspect_apj


def artifact(image_blob=b'synthetic firmware', **overrides):
    fields = {'magic': 'APJFWv1', 'board_id': 1234, 'board_revision': 0,
              'image_size': len(image_blob),
              'image': base64.b64encode(zlib.compress(image_blob)).decode()}
    fields.update(overrides)
    return json.dumps(fields).encode()


class FirmwareArtifactTests(unittest.TestCase):
    def test_board_size_and_hash_report_without_execution(self):
        data = artifact()
        result = inspect_apj(data, 1234, expected_sha256=hashlib.sha256(data).hexdigest())
        self.assertEqual(result['board_id'], 1234)
        self.assertEqual(result['image_sha256'], hashlib.sha256(b'synthetic firmware').hexdigest())
        self.assertFalse(result['signature_verified'])

    def test_mismatched_board_or_hash_rejects(self):
        with self.assertRaises(ValueError):
            inspect_apj(artifact(), 50)
        with self.assertRaises(ValueError):
            inspect_apj(artifact(), 1234, expected_sha256='0' * 64)

    def test_duplicate_json_keys_reject(self):
        data = artifact().replace(b'"board_id": 1234', b'"board_id": 50, "board_id": 1234')
        with self.assertRaises(ValueError):
            inspect_apj(data, 1234)

    def test_malformed_and_nonfinite_fields_reject(self):
        for kwargs in ({'board_id': True}, {'magic': 'PX4FWv1'}, {'image_size': True},
                       {'image_size': 999}, {'image': '!invalid!'}, {'board_revision': -1}):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                inspect_apj(artifact(**kwargs), 1234)

    def test_truncated_or_trailing_compression_rejects(self):
        compressed = zlib.compress(b'synthetic firmware')
        for value in (compressed[:-1], compressed + b'trailing'):
            with self.assertRaises(ValueError):
                inspect_apj(artifact(image=base64.b64encode(value).decode()), 1234)

    def test_decompression_is_bounded_even_if_declared_size_lies(self):
        with self.assertRaises(ValueError):
            inspect_apj(artifact(b'x' * 10000, image_size=10), 1234, max_image_bytes=100)

    def test_expected_identity_requires_positive_integer(self):
        for board in (True, 0, -1, '1234'):
            with self.assertRaises(ValueError):
                inspect_apj(artifact(), board)
