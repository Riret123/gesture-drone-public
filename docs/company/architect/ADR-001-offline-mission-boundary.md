# ADR 001: mission evaluation remains offline

Status: accepted for the toy simulator only, round 02.

Mission files describe local positions and dwell, not FC operations. The evaluator
must not translate `complete` into landing, arming, mode selection or disarming.
Neither successful parse nor successful interpolation is an authorization token.

The alternative of publishing existing `/flight_cmd` strings from mission points
is rejected: those strings request high-level takeoff/land and do not implement
waypoint tracking. Reusing them would imply capabilities absent from the bridge.

Dependencies flow `mission_cli -> mission_schema + mission_simulation`;
`mission_simulation -> mission_schema + validation`. No reverse import from a ROS
wrapper is introduced. Existing source-boundary tests enforce no ROS imports.

Acceptance: CLI rejects `--send`; summary identifies `flight_validated:false` and
`obstacles_modelled:false`; no entry-point rewiring or live parameters changed.
Future integration requires a separate reviewed controller, state freshness,
frame binding, obstacle policy, FC prerequisites and isolated SITL evidence.
