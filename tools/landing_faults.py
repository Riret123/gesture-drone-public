"""Print offline fault-campaign results; no flight or network I/O."""
import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src/gesture_control'))
from gesture_control.faults import campaign

if __name__ == '__main__':
    result = campaign()
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if all(result.values()) else 1)
