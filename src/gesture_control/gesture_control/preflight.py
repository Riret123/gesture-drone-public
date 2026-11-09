"""Conservative offline test-readiness checklist, not flight authorization."""
import json
import argparse

REQUIRED = ('simulation', 'physical_fc_isolated', 'sitl_endpoint_verified',
            'independent_operator', 'failsafes_reviewed', 'home_valid',
            'battery_checked', 'area_clear')


def report(inputs: dict) -> dict:
    checks = {key: inputs.get(key) is True for key in REQUIRED}
    return {'result': 'PASS' if all(checks.values()) else 'FAIL', 'checks': checks}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSON object file; boolean true only')
    args = parser.parse_args(argv)
    with open(args.input, encoding='utf-8') as source:
        inputs = json.load(source)
    if not isinstance(inputs, dict):
        parser.error('input must be an object')
    result = report(inputs)
    print(json.dumps(result, indent=2))
    return 0 if result['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
