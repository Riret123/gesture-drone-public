import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.gesture_classifier import classify_gesture, FINGER_TIP_MCP


class ClassifierTests(unittest.TestCase):
    def test_finger_counts(self):
        for count in range(6):
            points = [SimpleNamespace(x=0.0, y=0.0) for _ in range(21)]
            for index, (tip, mcp) in enumerate(FINGER_TIP_MCP):
                points[mcp] = SimpleNamespace(x=1.0, y=0.0)
                points[tip] = SimpleNamespace(x=3.0 if index < count else 0.8, y=0.0)
            # Wrist and MCP points define palm center; folded tips sit at it.
            with self.subTest(count=count):
                expected = 'fist' if count == 0 else 'open_palm' if count >= 4 else 'other'
                self.assertEqual(classify_gesture(points), expected)
