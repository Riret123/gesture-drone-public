# Offline policy inventory and limits

All modules below are experiments inside gesture_control; none is wired into the
live gesture node or flight bridge. Units and individual bounds live in module
docstrings. Run `python -B tests/run_all.py` for the complete portable suite.

| Area | Modules | Missing integration/evidence |
| --- | --- | --- |
| Landing | landing, frames, contact, faults | detector, calibration, contact hardware, FC adapter, SITL |
| Rover | rover, protocol, receiver | localization, obstacle avoidance, authenticated link, motor driver |
| Safety proposals | geofence, battery, arbitration, deadman, freshness, slew | valid home/RTL, state guards, reviewed live adapters |
| Vision | extended_gestures, velocity, follow, pantilt, filters, dataset | camera datasets, tuning, extrinsics, actuator validation |
| Observability | recording, history, diagnostics, mock_server | real telemetry read-only adapter, clock/transport delay accounting |
| Setup | configuration, preflight | actual dependency lock, Linux/ROS environment and measurements |

Codex ideas add local freshness, replay rejection, right-handed frame validation,
contact dwell, acceleration bounds, health summaries, bounded history, fault
campaign, strict offline settings and source/link checks. Each is independently
testable and deliberately makes no claim to protect a running vehicle.

`OfflineConfig.from_dict` is the validated config factory; direct dataclass
construction is not a file loader. No config file is automatically read.
Receiver session reset must be explicit while stopped. Numeric lexical forms in
the CRC envelope must match the encoder. Contact evidence does not disarm motors.
Filters add latency; a slew limiter must never delay a safety stop.
