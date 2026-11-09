# Portable command audit: Round 02 snapshot

Environment: Windows PowerShell checkout, Python 3.12 documented by prior environment inspection. Commands ran from the repository root with bytecode disabled. This is a historical snapshot, not a guarantee after later source changes.

| Command | Observed result | Limit |
| --- | --- | --- |
| `python -B tools/landing_faults.py` | exit 0; lost_tag, invalid_height, nonfinite_pose, false_contact, lateral_error_stops_descent all true | proposal-level fixtures, not FC response |
| `python -B tools/simulate_landings.py` | exit 0; 100 trials / 100 model successes | toy kinematics only, not a real success-rate claim |
| `python -B tools/company_docs_audit.py` | exit 0; 0 source issues before later hardening | source policy only, not rendering |
| `python -B tests/run_all.py` | most recent observed pre-site-fix snapshot: 276 passed, exit 0 | changing shared tree; later batches rerun |

Two shared regressions appeared during this batch and were reported to the owning workers: a telemetry parity Unicode fixture mismatch, and floating-point time equality in separation tests. They were corrected before the observed 276-pass run. Do not erase the failed observations from the central log.

The first RU/glossary write lost Unicode through PowerShell's pipeline. Actual Cyrillic was restored through the patch tool; encoding regressions now guard those artifacts. This does not establish translation quality.

Not run: ROS/ament/colcon, camera, SITL, real flight, Quest, browser rendering or target Linux/ARM installation. Re-run commands after changes; do not reuse this table as current proof.
