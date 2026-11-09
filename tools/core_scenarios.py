"""Print reviewed SITL plans; optionally run inert mock contracts on Windows."""
import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/drone_bringup'))
from drone_bringup.sitl_scenarios import SCENARIOS, plan, run_scenario


class InertTransport:
    """Acceptance stub only: no physics, MAVLink, ROS or actual observations."""
    def command(self, value):
        return True

    def fault(self, value):
        return True

    def expect(self, condition, timeout):
        return True


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenario', choices=SCENARIOS)
    parser.add_argument('--mock-contract', action='store_true')
    args = parser.parse_args(argv)
    result = {'scenario': args.scenario, 'steps': plan(args.scenario),
              'execution': 'none; plan only', 'sitl_validated': False}
    if args.mock_contract:
        result['mock_contract'] = run_scenario(args.scenario, InertTransport())
        result['execution'] = 'inert mock only; no flight dynamics'
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
