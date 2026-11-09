"""Run portable tests between source manifests; no git, ROS or hardware actions.

This detects endpoint drift, not transient edits restored between hashes and not
an immutable snapshot. Stop other writers before using results for acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REVIEWED_ROOTS = ('src', 'tests', 'tools', 'scripts/board', 'scripts/sitl', 'config')
ROOT_FILES = ('gesture_test.py', 'video_stream_server.py',
              'test_flight_cmd_bridge.py', 'viewer.html')


def source_manifest(root):
    root = Path(root).resolve()
    result = {}
    def record(path):
        if path.is_symlink():
            raise ValueError('source symlinks require independent review')
        resolved = path.resolve()
        if not resolved.is_relative_to(root):
            raise ValueError('source path escapes workspace')
        name = path.relative_to(root).as_posix()
        if name.startswith(('network/', 'docs/life_plan/', '.git/')):
            raise ValueError('forbidden source root')
        result[name] = hashlib.sha256(path.read_bytes()).hexdigest()

    for relative in REVIEWED_ROOTS:
        directory = root / relative
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError('required source directory missing')
        for path in sorted(directory.rglob('*')):
            if '__pycache__' in path.parts or path.suffix in ('.pyc', '.pyo'):
                continue
            if path.is_symlink():
                raise ValueError('source symlinks require independent review')
            if not path.is_file():
                continue
            record(path)
    for name in ROOT_FILES:
        record(root / name)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest-only', action='store_true')
    args = parser.parse_args(argv)
    before = source_manifest(ROOT)
    if args.manifest_only:
        print(json.dumps(before, indent=2, sort_keys=True))
        return 0
    code = subprocess.call((sys.executable, '-B', str(ROOT / 'tests/run_all.py')), cwd=ROOT)
    after = source_manifest(ROOT)
    changed = sorted(name for name in before.keys() | after.keys()
                     if before.get(name) != after.get(name))
    print(json.dumps({'suite_exit': code, 'source_files': len(before),
                      'source_changed': changed,
                      'manifest_sha256': hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
                      'scope': 'portable tests; endpoint drift check, not immutable snapshot'}))
    return 0 if code == 0 and not changed else 1


if __name__ == '__main__':
    raise SystemExit(main())
