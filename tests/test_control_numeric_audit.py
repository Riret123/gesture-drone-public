from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.deadman import Deadman
from gesture_control.velocity import hand_velocity
from gesture_control.slew import SlewLimiter


class ControlNumericAuditTests(unittest.TestCase):
    def test_deadman_huge_clock_rejected_as_value_error(self):
        d=Deadman()
        with self.assertRaises(ValueError):
            d.update(False,True,0,10**10000)

    def test_deadman_invalid_clock_revokes_previous_release(self):
        d=Deadman()
        d.update(False,True,1,1)
        with self.assertRaises(ValueError):
            d.update(True,True,0,0)
        self.assertFalse(d.update(True,True,2,2))

    def test_deadman_boolean_config_and_clock_reject(self):
        with self.assertRaises(ValueError):
            Deadman(True)
        with self.assertRaises(ValueError):
            Deadman().update(False,True,0,True)

    def test_deadman_replayed_release_cannot_rearm(self):
        d=Deadman()
        d.update(False,True,0,0)
        self.assertFalse(d.update(True,True,0,0))
        self.assertFalse(d.update(True,True,.1,.1))

    def test_velocity_malformed_config_consistent(self):
        for limit,deadzone in [(True,.1),(10**10000,.1),(.2,'zero'),(.2,False)]:
            with self.assertRaises(ValueError):
                hand_velocity(.5,.5,limit=limit,deadzone=deadzone)

    def test_slew_strict_stop_boolean(self):
        with self.assertRaises(ValueError):
            SlewLimiter().update((0,0),.1,stop='false')

    def test_slew_malformed_target_types(self):
        for target in [None,1,'ab',[True,0],[10**10000,0]]:
            with self.assertRaises(ValueError):
                SlewLimiter().update(target,.1)

    def test_slew_boolean_dt_and_config_reject(self):
        with self.assertRaises(ValueError):
            SlewLimiter().update((0,0),True)
        with self.assertRaises(ValueError):
            SlewLimiter(speed=True)

    def test_slew_underflow_does_not_divide_by_zero(self):
        with self.assertRaises(ValueError):
            SlewLimiter(acceleration=5e-324).update((1,0),.1)

    def test_slew_finite_large_target_retains_direction(self):
        result=SlewLimiter(acceleration=1,speed=.2).update((1e308,1e308),1)
        self.assertGreater(result[0],0)
        self.assertAlmostEqual(result[0],result[1])
        self.assertAlmostEqual(sum(v*v for v in result)**.5,.2)
