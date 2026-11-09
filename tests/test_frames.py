import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))

import unittest
from gesture_control.frames import transform


class FrameTests(unittest.TestCase):
    def test_rotation_translation(self):
        rotation = ((0, -1, 0), (1, 0, 0), (0, 0, 1))
        self.assertEqual(transform((1, 2, 3), rotation, (10, 0, 0)), (8, 1, 3))
        for bad in (((2, 0, 0), (0, 1, 0), (0, 0, 1)),
                    ((-1, 0, 0), (0, 1, 0), (0, 0, 1))):
            with self.assertRaises(ValueError):
                transform((1, 2, 3), bad, (0, 0, 0))
