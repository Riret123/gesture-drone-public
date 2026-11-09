from pathlib import Path
import sys
import unittest
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.telemetry_contract import normalize_telemetry, decode_telemetry


class TelemetryNumericAttackTests(unittest.TestCase):
    def test_huge_integer_never_escapes_numeric_validation(self):
        sample = dict(schema=1, mock=True, age=0, mode='SIM', battery=10**10000,
                      deadman=False, acks=[])
        self.assertEqual(normalize_telemetry(sample, 0, 0, 1).status, 'INVALID')


class TelemetryDecodeTests(unittest.TestCase):
    def source(self):
        return json.dumps(dict(schema=1, mock=True, age=0, mode='SIM', battery=50,
                               deadman=False, acks=[]))

    def test_utf8_roundtrip(self):
        source = self.source().replace('SIM', 'СИМУЛЯЦИЯ')
        for value in (source, source.encode('utf-8')):
            self.assertEqual(decode_telemetry(value, 0, 0, 1).status, 'MOCK')

    def test_duplicate_keys_rejected_even_when_values_agree(self):
        source = self.source().replace('"schema": 1', '"schema": 1, "schema": 1')
        self.assertEqual(decode_telemetry(source, 0, 0, 1).status, 'INVALID')

    def test_nonstandard_constants_and_huge_exponent(self):
        for token in ['NaN', 'Infinity', '-Infinity', '1e9999']:
            source = self.source().replace('"battery": 50', '"battery": ' + token)
            self.assertEqual(decode_telemetry(source, 0, 0, 1).status, 'INVALID')

    def test_malformed_utf8_surrogate_and_bom(self):
        for source in [b'\xff', '\ud800', '\ufeff' + self.source(), b'\xef\xbb\xbf{}']:
            self.assertEqual(decode_telemetry(source, 0, 0, 1).status, 'INVALID')

    def test_character_and_byte_budgets(self):
        source = self.source()
        self.assertEqual(decode_telemetry(source, 0, 0, 1,
                                         max_bytes=len(source)).status, 'MOCK')
        self.assertEqual(decode_telemetry(source, 0, 0, 1,
                                         max_bytes=len(source)-1).status, 'INVALID')
        non_ascii = source.replace('SIM', '中' * 10)
        self.assertEqual(decode_telemetry(non_ascii, 0, 0, 1,
                                         max_bytes=len(non_ascii)).status, 'INVALID')

    def test_depth_and_wrong_top_level(self):
        for source in ['[' * 1100 + '0' + ']' * 1100, '[]', 'null', 'true', '"text"']:
            self.assertEqual(decode_telemetry(source, 0, 0, 1).status, 'INVALID')

    def test_limits_are_configuration_not_payload(self):
        for value in [True, 0, -1, 1048577, 1.5]:
            with self.assertRaises(ValueError):
                decode_telemetry('{}', 0, 0, 1, max_bytes=value)
