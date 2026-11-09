# Gesture drone

A gesture-triggered drone prototype with ROS 2 / MAVROS / ArduPilot, plus portable
Python experiments for a future mobile landing pad. This repository demonstrates
control software structure and testing; it does not demonstrate autonomous navigation
or validated hardware precision landing.

```text
Camera -> OpenCV/MediaPipe -> debounce + gesture safety -> /flight_cmd
                                                        |
                       /flight_cmd_ack <- flight bridge -> MAVROS -> ArduPilot

OFFLINE: marker pose -> landing state machine -> toy moving-rover simulation
         landmark fixtures -> filters / gesture evaluation / velocity proposals
         telemetry fixture -> read-only dashboard / Quest overlay
```

## Features and evidence

- Existing ROS gesture path: open palm selects GUIDED, arms and requests 2 m
  takeoff; fist/land/emergency request landing; hold selects LOITER.
- Five-frame debounce and missing-input hold/land policy; see [safety limits](docs/SAFETY.md).
- Pure-Python experiments: precision landing proposals, differential rover drive,
  CRC protocol, geofence, battery hysteresis, command arbitration, Quest deadman,
  PID following, landmark filters and bilingual command parsing. These are not
  connected to flight control.
- Portable unittest suite, 100-seed toy simulation, CSV/JSONL recorder/replay,
  buildless read-only telemetry pages and disabled rover firmware skeleton.

## Run offline on Windows or Linux

Python 3.12, standard library only:

```text
python -B tests/run_all.py
python -B tools/simulate_landings.py
```

To run package tools without installing ROS, set PYTHONPATH to
`src/gesture_control` (PowerShell: `$env:PYTHONPATH='src/gesture_control'`;
Bash: `export PYTHONPATH=src/gesture_control`). Then:

```text
python -B -m gesture_control.mock_server
python -B -m gesture_control.dronectl hold
```

The mock dashboard is at http://127.0.0.1:8081 and Quest view at /quest. dronectl
defaults to dry run. No software here should be treated as permission to arm hardware.

## ROS / SITL deployment

Target described in source: Orange Pi 5 Pro, AERO SELFIE H743, ROS 2 Jazzy,
MAVROS and ArduPilot. Actual target installation and physical wiring are unverified.
OpenCV/MediaPipe are external dependencies; no reproducible version lock exists.
See [board validation](docs/TESTING_ON_BOARD.md) and AGENTS.md for sourced Linux
workspace build steps. Build both ROS packages before starting bridge and gesture
nodes. Confirm SITL UDP routing and physically isolate flight controllers first.
Never run the live integration script against hardware.

## Safety and next steps

Never arm real motors in automated tests. Remove props and disconnect motor power
for bench inspection; props off does not authorize arming. Acknowledgements mean
service acceptance, not completed flight. Companion policies do not replace FC
failsafes, a competent independent pilot, valid airspace or operator authorization.

Start with [architecture](docs/ARCHITECTURE.md), [roadmap](docs/ROADMAP.md),
[landing concept](docs/LANDING_PLATFORM.md), [test log](docs/NIGHT_LOG.md),
[backlog](docs/BACKLOG.md), and [BOM](docs/BOM.md).

## How this was built (AI assistance)

This is a student project by Emir (University of Arizona, aerospace engineering).
The hardware choices, system design, SITL/board bring-up and the gesture-to-flight
chain are the author's own work. Many of the offline Python modules, tests and
documents in this repository (landing-pad experiments, simulators, `docs/company/`
planning notes, the static `docs/site/`) were generated with AI coding assistants
(OpenAI Codex, Anthropic Claude) under the author's direction and then run through
the unittest suite. They are prototypes: treat everything not marked as verified
in `docs/core/STATUS.md` as untested on real hardware.
