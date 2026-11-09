"""Adversarial validation of legacy offline policies, never live ROS wrappers."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.arbitration import Arbiter
from gesture_control.battery import BatteryPolicy
from gesture_control.contact import ContactConfirmation
from gesture_control.diagnostics import COMPONENTS, diagnose
from gesture_control.freshness import Freshness
from gesture_control.geofence import evaluate
from gesture_control.history import TelemetryHistory

BAD = (True, None, '1', [], {}, float('nan'), float('inf'), 10 ** 1000)


class LegacyArbiterValidationTests(unittest.TestCase):
    def test_timeout_strict_types(self):
        for bad in BAD:
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                Arbiter(bad)

    def test_malformed_source_command_cannot_poison_clock(self):
        for source, command in (([], 'hold'), ('gesture', []), ('unknown', 'land')):
            arbiter = Arbiter()
            arbiter.submit('gesture', 'open_palm', 0)
            with self.subTest(source=source, command=command), self.assertRaises(ValueError):
                arbiter.submit(source, command, 100)
            self.assertEqual(arbiter.choose(.1), 'open_palm')

    def test_clock_rejects_malformed_and_negative(self):
        for bad in BAD + (-1,):
            arbiter = Arbiter()
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                arbiter.choose(bad)


class LegacyBatteryValidationTests(unittest.TestCase):
    def test_threshold_configuration_strict_types(self):
        for field in ('low', 'critical', 'hysteresis'):
            for bad in BAD:
                with self.subTest(field=field, bad=type(bad)), self.assertRaises(ValueError):
                    BatteryPolicy(**{field: bad})

    def test_invalid_measurement_holds_without_erasing_latch(self):
        policy = BatteryPolicy()
        self.assertEqual(policy.update(13, 4), 'land')
        for bad in BAD:
            with self.subTest(bad=type(bad)):
                self.assertEqual(policy.update(bad, 4), 'hold')
                self.assertEqual(policy.state, 'critical')

    def test_huge_cell_count_does_not_throw(self):
        policy = BatteryPolicy()
        self.assertEqual(policy.update(14, 10 ** 1000), 'hold')
        self.assertEqual(policy.update(5e-324, 10**300), 'hold')

    def test_recovery_margin_cannot_overflow_or_disappear(self):
        for low, critical, margin in ((1e308, 5e307, 1e308), (3.5, 3.3, 5e-324)):
            with self.subTest(margin=margin), self.assertRaises(ValueError):
                BatteryPolicy(low, critical, margin)


class LegacyGeofenceValidationTests(unittest.TestCase):
    def test_invalid_configuration_rejected_consistently(self):
        for field in ('radius', 'ceiling', 'rtl_percent'):
            for bad in BAD:
                with self.subTest(field=field, bad=type(bad)), self.assertRaises(ValueError):
                    evaluate(0, 0, 1, 90, **{field: bad})

    def test_invalid_telemetry_requests_hold(self):
        for index in range(4):
            for bad in BAD:
                values = [0, 0, 1, 90]
                values[index] = bad
                with self.subTest(index=index, bad=type(bad)):
                    self.assertEqual(evaluate(*values), 'hold')


class LegacyFreshnessValidationTests(unittest.TestCase):
    def test_timeout_strict_types(self):
        for bad in BAD:
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                Freshness(bad)

    def test_clock_strict_types(self):
        for bad in BAD + (-1,):
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                Freshness().receive(bad)

    def test_nonrepresentable_deadline_is_not_fresh(self):
        policy = Freshness(.1)
        policy.receive(1e16)
        self.assertFalse(policy.fresh(1e16))
        policy = Freshness(1e308)
        policy.receive(1e308)
        self.assertFalse(policy.fresh(1e308))


class LegacyContactValidationTests(unittest.TestCase):
    def test_limits_strict_types(self):
        for field in ('dwell', 'max_height'):
            for bad in BAD:
                with self.subTest(field=field, bad=type(bad)), self.assertRaises(ValueError):
                    ContactConfirmation(**{field: bad})

    def test_height_strict_types_reset_dwell(self):
        for bad in BAD:
            policy = ContactConfirmation()
            policy.update(True, .1, 0)
            with self.subTest(bad=type(bad)):
                self.assertFalse(policy.update(True, bad, .2))
                self.assertFalse(policy.update(True, .1, .3))

    def test_clock_strict_types(self):
        for bad in BAD + (-1,):
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                ContactConfirmation().update(True, .1, bad)

    def test_subresolution_dwell_is_not_contact(self):
        policy = ContactConfirmation(dwell=.3)
        self.assertFalse(policy.update(True, .1, 1e16))
        self.assertFalse(policy.update(True, .1, 1e16))


class LegacyHistoryValidationTests(unittest.TestCase):
    def test_battery_strict_types(self):
        for bad in BAD:
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                TelemetryHistory().update('LOITER', bad, False, 0)

    def test_clock_strict_types(self):
        for bad in BAD + (-1,):
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                TelemetryHistory().snapshot(bad)

    def test_invalid_update_does_not_advance_clock(self):
        history = TelemetryHistory()
        history.update('LOITER', 90, False, 1)
        with self.assertRaises(ValueError):
            history.update('LOITER', True, False, 100)
        self.assertEqual(history.snapshot(2)['battery'], 90)


class LegacyDiagnosticsValidationTests(unittest.TestCase):
    def test_timeout_strict_types(self):
        for bad in BAD:
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                diagnose({}, True, False, bad)

    def test_invalid_age_is_missing_or_stale(self):
        for bad in BAD:
            ages = dict.fromkeys(COMPONENTS, 0)
            ages['camera'] = bad
            with self.subTest(bad=type(bad)):
                report = diagnose(ages, True, False)
                self.assertFalse(report['healthy'])
                self.assertEqual(report['components']['camera'], 'missing_or_stale')

    def test_nonmapping_age_container_rejected(self):
        for bad in (None, [], 'ages', True):
            with self.subTest(bad=type(bad)), self.assertRaises(ValueError):
                diagnose(bad, True, False)
