# Offline waypoint planner and simulator

After package installation, run from the workspace root:

```bash
python3 -m gesture_control.mission_cli docs/company/backend/examples/inspection_square.json --summary-only
python3 -m gesture_control.mission_cli docs/company/backend/examples/dwell_only.json --interval 0.25
```

The first example reports 9 metres of idealized travel, 5 seconds of dwell and
50 seconds total at 0.2 m/s. It ends overhead at height 1 metre in its mathematical
coordinate frame. It does not land, contact a vehicle or command a camera.
The second example remains at origin for two seconds and then marks complete.
`rejected_boundary.json` intentionally fails because its point touches the fence.

The command reads an explicitly supplied file as UTF-8, at most 65,536 bytes.
Use `-` to read bounded binary stdin. Output is JSON on stdout; invalid input and
read errors produce a short category on stderr and exit status 2. Unknown options,
including `--send`, fail in argument parsing. Successful offline evaluation exits 0.

Sampling flags: `--interval` seconds, `--max-duration` seconds, `--max-samples`
count. `--summary-only` avoids timeline allocation and ignores the *count needed*
for a timeline, but still validates configuration types/domains. Full timelines
include zero and the exact final duration once. Changing sample interval changes
the grid, not the analytic trajectory or its duration.

Schema requires integer version 1, frame `local_enu`, and a nonempty `waypoints`
array. Each point requires `name,east,north,up`; `dwell` defaults to zero. Plan
`speed,radius,ceiling` default to 0.2, 20, 5 respectively. Units are metres and
seconds. These are offline toy values, not proposed changes to the live bridge.

No acceleration, wind, terrain, obstacle, localization error, energy reserve,
control latency or flight-controller behavior is modeled. Never interpret a
complete toy mission as evidence that the route is safe or physically achievable.
