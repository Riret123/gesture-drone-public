#!/usr/bin/env bash
# Plan by default. Explicit guarded execution is available only for isolated SITL.
set -euo pipefail
scenario=${1:?choose takeoff, hold, land, emergency or rc-loss}
shift
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)
exec python3 "$root/tools/sitl_ros_scenarios.py" "$scenario" "$@"
