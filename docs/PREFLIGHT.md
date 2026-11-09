# Offline SITL readiness report

Run `python -m gesture_control.preflight inputs.json` with the package on PYTHONPATH.
The JSON object requires boolean true for simulation, physical_fc_isolated,
sitl_endpoint_verified, independent_operator, failsafes_reviewed, home_valid,
battery_checked, area_clear. Missing/false/non-boolean values fail. Exit 0 is PASS;
1 is FAIL. These are operator attestations, not sensor measurements.

PASS means this checklist is complete, never permission to fly hardware. Verify
SITL UDP routing and isolation before any command. For bench inspection remove
props and disconnect motor power; do not arm. Follow SAFETY.md. This script cannot
verify wiring, pilot competence, airspace, environment or FC-level failsafes.
