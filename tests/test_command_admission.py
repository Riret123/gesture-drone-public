import unittest
from drone_bringup.command_admission import CommandAdmission


class CommandAdmissionTests(unittest.TestCase):
    def test_flood_is_bounded_and_land_has_reserved_lane(self):
        gate = CommandAdmission()
        self.assertTrue(gate.is_idle())
        takeoff = gate.acquire('open_palm')
        self.assertFalse(gate.is_idle())
        self.assertIsNotNone(takeoff)
        for _ in range(10000):
            self.assertIsNone(gate.acquire('open_palm'))
        hold = gate.acquire('hold')
        land = gate.acquire('emergency')
        self.assertIsNotNone(hold)
        self.assertIsNotNone(land)
        self.assertIsNone(gate.acquire('fist'))
        gate.release(takeoff)
        self.assertIsNone(gate.acquire('open_palm'))
        gate.release(hold)
        self.assertFalse(gate.is_idle())
        self.assertIsNone(gate.acquire('hold'))
        gate.release(land)
        self.assertTrue(gate.is_idle())
        self.assertIsNotNone(gate.acquire('open_palm'))

    def test_old_release_cannot_unlock_new_lease(self):
        gate = CommandAdmission()
        old = gate.acquire('land')
        gate.release(old)
        new = gate.acquire('land')
        gate.release(old)
        self.assertIsNone(gate.acquire('emergency'))
        self.assertFalse(gate.is_idle())
        gate.release(new)
        self.assertIsNotNone(gate.acquire('land'))

    def test_unknown_input_has_no_worker(self):
        gate = CommandAdmission()
        for value in ('other', '', None, [], True):
            self.assertIsNone(gate.acquire(value))
