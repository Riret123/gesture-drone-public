"""Record explicit labeled landmark JSONL as CSV; no camera or image capture."""
import argparse
import json
from .dataset import record


def convert(source, destination) -> int:
    def samples():
        for line in source:
            row = json.loads(line)
            if not isinstance(row, dict) or set(row) != {'label', 'points'}:
                raise ValueError('expected label and points only')
            yield row['label'], row['points']
    return record(destination, samples())


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', help='JSONL: label and 21 x/y pairs per line')
    parser.add_argument('output', help='new CSV path; refuses overwrite')
    args = parser.parse_args(argv)
    with open(args.input, encoding='utf-8') as source:
        # Validate before creating output; never overwrite an existing dataset.
        import io
        buffer = io.StringIO(newline='')
        count = convert(source, buffer)
    with open(args.output, 'x', encoding='utf-8', newline='') as destination:
        destination.write(buffer.getvalue())
    print(f'Recorded {count} landmark samples; no images')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
