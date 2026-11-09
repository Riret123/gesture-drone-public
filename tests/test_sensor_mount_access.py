import sys
from pathlib import Path
from dataclasses import replace
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.sensor_mount_geometry import MountGeometry
from gesture_control.sensor_mount_access import check_access


class AccessTests(unittest.TestCase):
    def setUp(self):
        self.mount = MountGeometry(40, 30, 4, 2, 2, ((10, 10), (30, 20)))
        self.limits = dict(head_diameter_mm=8, tool_diameter_mm=10, access_clearance_mm=1)

    def test_sufficient_access(self):
        self.assertEqual(check_access(self.mount, **self.limits), ())

    def test_e27_hole_can_fit_while_tool_envelope_fails(self):
        mount = replace(self.mount, holes_xy_mm=((4, 4),))
        self.assertIn(('access_edge_clearance', 0), check_access(mount, **self.limits))

    def test_separate_holes_can_have_overlapping_tool_envelopes(self):
        mount = replace(self.mount, holes_xy_mm=((10, 10), (18, 10)))
        self.assertIn(('access_overlap', 0, 1), check_access(mount, **self.limits))

    def test_invalid_access_dimensions_and_head_model(self):
        for changes in ({'head_diameter_mm': 3}, {'tool_diameter_mm': True},
                        {'access_clearance_mm': 0}, {'head_diameter_mm': float('inf')}):
            with self.assertRaises(ValueError):
                check_access(self.mount, **(self.limits | changes))

    def test_base_geometry_findings_preserved(self):
        mount = replace(self.mount, holes_xy_mm=((2, 2),))
        result = check_access(mount, **self.limits)
        self.assertIn(('edge_clearance', 0), result)
        self.assertIn(('access_edge_clearance', 0), result)
