import sys
from pathlib import Path
from dataclasses import replace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.sensor_mount_geometry import MountGeometry, validate_mount


class MountTests(unittest.TestCase):
    def setUp(self):
        self.mount = MountGeometry(40, 30, 4, 2, 2, ((4, 4), (36, 26)))

    def test_exact_edge_clearance_accepts(self):
        self.assertEqual(validate_mount(self.mount), ())

    def test_e05_hole_edge_not_centre_controls_clearance(self):
        findings = validate_mount(replace(self.mount, holes_xy_mm=((2, 4),)))
        self.assertIn(('edge_clearance', 0), findings)

    def test_overlap_gap_and_exact_boundary(self):
        self.assertIn(('hole_gap', 0, 1),
                      validate_mount(replace(self.mount, holes_xy_mm=((4, 4), (9, 4)))))
        self.assertEqual(validate_mount(replace(self.mount, holes_xy_mm=((4, 4), (10, 4)))), ())

    def test_duplicate_and_impossible_plate(self):
        self.assertIn(('hole_gap', 0, 1), validate_mount(replace(self.mount, holes_xy_mm=((4, 4), (4, 4)))))
        self.assertIn(('edge_clearance', 0), validate_mount(replace(self.mount, width_mm=3)))

    def test_invalid_dimensions_centres_and_bound(self):
        for value in (True, 0, -1, float('nan'), float('inf')):
            with self.assertRaises(ValueError):
                validate_mount(replace(self.mount, width_mm=value))
        for centres in ([], (), ((True, 1),), ((1, 2, 3),), ((4, 4),) * 65):
            with self.assertRaises(ValueError):
                validate_mount(replace(self.mount, holes_xy_mm=centres))
