"""A diagnostic must not turn contradictory FC observations into a pass."""
import unittest
from drone_bringup.doctor import connected_disarmed


class DoctorStateAmbiguityTests(unittest.TestCase):
    def test_invalid_yaml_scalar_shapes_and_stamp_ranges_fail(self):
        baseline = 'connected: true\narmed: false\n'
        for extra in ('mode: [GUIDED', 'mode: {invalid}', 'mode: !tag GUIDED',
                      'mode: ', 'header:\n  frame_id: [invalid]',
                      'header:\n  stamp:\n    sec: 2147483648'):
            self.assertFalse(connected_disarmed(baseline + extra))
        for mode in ('GUIDED', '"GUIDED"', "'GUIDED'", "''"):
            self.assertTrue(connected_disarmed(baseline + 'mode: ' + mode))

    def test_state_fields_cannot_be_spliced_across_documents_or_nested(self):
        for output in ('connected: true\n---\narmed: false',
                       'header:\n  connected: true\narmed: false',
                       'connected: true\n  armed: false',
                       'connected: true\narmed: false\nunknown: data',
                       'connected: true\narmed: false\n---\nmode: LAND',
                       'connected: true\narmed: false\nheader:\n  stamp:\n    nanosec: 1000000000'):
            self.assertFalse(connected_disarmed(output))

    def test_one_explicit_connected_disarmed_sample(self):
        self.assertTrue(connected_disarmed(
            'header:\n  stamp:\n    sec: 123\nconnected: true\narmed: false\nmode: STABILIZE\n---\n'))

    def test_duplicate_or_contradictory_fields_fail(self):
        baseline = 'connected: true\narmed: false\n'
        for extra in ('armed: true', 'armed: false', 'connected: false',
                      'connected: true', '---\n' + baseline):
            with self.subTest(extra=extra):
                self.assertFalse(connected_disarmed(baseline + extra))

    def test_missing_malformed_and_oversized_output_fails(self):
        for output in (None, '', 'connected: true', 'armed: false',
                       'connected: True\narmed: false',
                       'connected: true\narmed: 0',
                       'connected: false\narmed: false',
                       'connected: true\narmed: true',
                       'connected: true\narmed: false\n' + ' ' * 16385):
            with self.subTest(output=repr(output)[:80]):
                self.assertFalse(connected_disarmed(output))
