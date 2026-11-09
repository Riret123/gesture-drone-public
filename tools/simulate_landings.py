"""Run 100 reproducible toy landings without ROS, camera or hardware."""
import sys
from pathlib import Path
import json
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.simulation import batch

if __name__ == '__main__':
    print(json.dumps(batch(), indent=2))
