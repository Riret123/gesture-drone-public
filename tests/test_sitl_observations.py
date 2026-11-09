import unittest
from drone_bringup.sitl_observations import ScenarioObservations, ObservationLimits


class SitlObservationsTests(unittest.TestCase):
    def setUp(self):
        self.obs = ScenarioObservations()

    def feed(self, now, armed=False, mode='STABILIZE', altitude=0., landed=1,
             position=(0., 0., 0.)):
        self.obs.update_state(True, armed, mode, now)
        self.obs.update_altitude(altitude, now)
        self.obs.update_landed(landed, now)
        self.obs.update_position(position, now)

    def test_disarmed_requires_ground_and_fresh_telemetry(self):
        self.assertFalse(self.obs.ready('connected_disarmed', 0.))
        self.feed(1.)
        self.assertTrue(self.obs.ready('connected_disarmed', 1.))
        self.assertFalse(self.obs.ready('connected_disarmed', 3.))

    def test_takeoff_ack_cannot_replace_airborne_observation(self):
        self.feed(1., armed=True, mode='GUIDED')
        self.assertFalse(self.obs.ready('airborne_at_target', 1.))
        self.feed(2., armed=True, mode='GUIDED', altitude=2., landed=2)
        self.assertTrue(self.obs.ready('airborne_at_target', 2.))

    def test_hold_requires_dwell_and_new_position_samples(self):
        self.feed(1., armed=True, mode='LOITER', altitude=2., landed=2)
        self.assertFalse(self.obs.ready('loiter_stable', 1.))
        self.assertFalse(self.obs.ready('loiter_stable', 1.5))
        self.feed(2., armed=True, mode='LOITER', altitude=2., landed=2)
        self.assertFalse(self.obs.ready('loiter_stable', 2.))
        self.feed(3., armed=True, mode='LOITER', altitude=2., landed=2)
        self.assertTrue(self.obs.ready('loiter_stable', 3.))

    def test_hold_drift_or_gap_resets_dwell(self):
        self.feed(1., armed=True, mode='LOITER', altitude=2., landed=2)
        self.obs.ready('loiter_stable', 1.)
        self.feed(2., armed=True, mode='LOITER', altitude=2., landed=2,
                  position=(1., 0., 0.))
        self.assertFalse(self.obs.ready('loiter_stable', 2.))
        self.assertFalse(self.obs.ready('loiter_stable', 5.))

    def test_landed_requires_disarm_and_ground_indication(self):
        self.feed(1., armed=True, mode='LAND', altitude=0., landed=1)
        self.assertFalse(self.obs.ready('landed_disarmed', 1.))
        self.feed(2., mode='LAND', landed=2)
        self.assertFalse(self.obs.ready('landed_disarmed', 2.))
        self.feed(3., mode='LAND')
        self.assertTrue(self.obs.ready('landed_disarmed', 3.))

    def test_invalid_sample_and_clock_revoke_readiness(self):
        self.feed(1.)
        self.obs.update_altitude(float('nan'), 1.1)
        self.assertFalse(self.obs.ready('connected_disarmed', 1.1))
        self.feed(2.)
        self.assertFalse(self.obs.ready('connected_disarmed', True))
        self.assertFalse(self.obs.ready('connected_disarmed', 1.))

    def test_rc_mode_is_explicit_and_never_inferred_from_ack(self):
        self.feed(1., armed=True, mode='GUIDED', altitude=2., landed=2)
        self.assertFalse(self.obs.ready('configured_rc_failsafe', 1.))
        self.obs.mark_rc_fault(1.5)
        self.feed(2., armed=True, mode='LAND', altitude=1., landed=2)
        self.assertTrue(self.obs.ready('configured_rc_failsafe', 2.))

    def test_rc_mode_before_injection_is_not_fault_evidence(self):
        self.feed(1., armed=True, mode='LAND', altitude=1., landed=2)
        self.assertFalse(self.obs.ready('configured_rc_failsafe', 1.))
        self.obs.mark_rc_fault(1.)
        self.assertFalse(self.obs.ready('configured_rc_failsafe', 1.))

    def test_hold_does_not_bridge_unobserved_telemetry_gap(self):
        for now in (1., 2.):
            self.feed(now, armed=True, mode='LOITER', altitude=2., landed=2)
            self.assertFalse(self.obs.ready('loiter_stable', now))
        self.feed(10., armed=True, mode='LOITER', altitude=2., landed=2)
        self.assertFalse(self.obs.ready('loiter_stable', 10.))

    def test_other_streams_cannot_hide_position_gap(self):
        for now in (1., 2.):
            self.feed(now, armed=True, mode='LOITER', altitude=2., landed=2)
            self.obs.ready('loiter_stable', now)
        for now in range(3, 10):
            self.obs.update_state(True, True, 'LOITER', float(now))
        self.feed(10., armed=True, mode='LOITER', altitude=2., landed=2)
        self.assertFalse(self.obs.ready('loiter_stable', 10.))

    def test_limits_reject_bad_values(self):
        for kwargs in ({'dwell_sec': True}, {'max_age_sec': 0}, {'target_m': 3.},
                       {'altitude_tolerance_m': float('inf')}, {'rc_mode': 'GUIDED'}):
            with self.assertRaises(ValueError):
                ObservationLimits(**kwargs)
