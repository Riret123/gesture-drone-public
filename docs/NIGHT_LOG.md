# Night log

## 2026-11-08 — Task 1: deployment workspace and Linux/ROS environment

- Changed: created this log because `docs/NIGHT_PLAN.md` is absent; followed
  the four TODOs in `AGENTS.md` in order.
- Checked: current workspace is
  `<repo>`; Python reports 3.12.13.
  Root directory inspection found no `ai_env`, `ardupilot_env`, or colcon
  build/install outputs. The documented `~/jedi_drone_ws` is a deployment
  path, not a confirmed path on the target.
- Blocked: target Linux host is unavailable. Cannot confirm its workspace,
  ROS Jazzy installation, sourced environment, or console-script interpreter.
  ROS/SITL builds and runtime tests were not run on Windows.
- Follow-up on target: record actual workspace path, OS/architecture, Python
  executable/version, ROS distribution and installed package versions before
  following the existing build instructions. Do not assume this checkout's
  Python version matches the target.

## 2026-11-08 — Task 2: reproducible dependencies and compatible versions

- Changed: appended dependency findings and unresolved validation here only.
- Checked: both `setup.py` files require only setuptools; package manifests
  declare ROS dependencies. OpenCV and MediaPipe are external dependencies;
  the node specifically uses `mp.solutions.hands`. No lockfile or bootstrap
  exists in the inspected source listing. `AGENTS.md` describes pyyaml,
  system-site-packages, historical MAVROS 2.14.0 and GeographicLib setup.
- Blocked: cannot derive a verified dependency lock from source declarations
  or historical notes. No speculative pins or installations were made.
  Linux/ARM wheel compatibility, ROS imports, GeographicLib data and camera
  operation cannot be tested on this Windows environment without ROS/SITL.
- Follow-up on target: capture working pip and OS/ROS package versions,
  confirm the required MediaPipe API and camera imports, then verify a clean
  environment rebuild before treating those versions as reproducible.

## 2026-11-08 — Task 3: external ArduPilot revision and prerequisites

- Changed: appended external-source findings and the outstanding evidence.
- Checked: no external `ardupilot/` checkout or `ardupilot_env` exists here.
  `AGENTS.md` documents separate environments and `empy==3.3.4`, but does
  not identify a verified external revision or full prerequisites.
- Blocked: external revision, submodule completeness, toolchain and SITL
  build cannot be confirmed from this checkout. No git commands, downloads,
  SITL launches or flight integration tests were run on Windows.
- Follow-up on target: obtain a recorded external source revision, submodule
  inventory, OS prerequisites and environment versions from the deployment
  owner; validate the documented build and disarmed SITL connection there.

## 2026-11-08 — Task 4: physical FC device, baud and wiring

- Changed: appended hardware findings and safety limitations.
- Checked: `mavros_apm.launch.py` defaults to `/dev/ttyUSB0:921600`, empty
  GCS routing and target IDs 1/1. These are source defaults, not measurements
  of physical hardware. No launch defaults or flight behavior were changed.
- Blocked: physical Orange Pi/FC and Linux serial enumeration are unavailable.
  Device identity, wiring, UART configuration and matched baud cannot be
  verified on Windows. ROS/SITL and hardware tests were not run.
- Follow-up: have the hardware owner verify board pinouts, voltage levels,
  serial identity and matching FC configuration. Remove propellers and keep
  motor power disconnected for bench inspection; this does not authorize
  arming. Never run the bridge integration test against physical hardware.

## Safety audit and validation limits

- Read `AGENTS.md`, the gesture node/classifier, bridge, launch wrapper,
  package manifests and setup declarations. No git commands were run and
  `network/` was not read or modified.
- The requested debounce, failsafe hold-to-land and two-fist emergency
  behaviors are absent from the inspected implementation: the node processes
  one hand (`max_num_hands=1`), publishes on gesture changes without a timed
  debounce, and returns on camera read failure. The bridge handles only
  `open_palm` and `fist`, with other commands acknowledged as no-ops.
  These are unresolved safety requirements, not validated safeguards.
- No flight parameters, thresholds, timeouts, modes, arming sequence,
  guards, failsafes or MAVLink routing were modified. No motors were armed.
- All four confirmation tasks remain blocked pending target evidence.
  This documentation-only change was checked against local source; no ROS,
  SITL, camera or hardware validation is claimed.
- Windows pure-Python check: `python -B -` ran an inline standard-library
  unittest against the actual classifier with synthetic landmarks for all
  six extended-finger counts (0 through 5). All six subcases passed:
  zero maps to fist, one through three to other, four/five to open palm.
  Bytecode writing was disabled. This checks classification only, not the
  missing safety behaviors or real camera recognition.

## 2026-11-08 Task 1: gesture safety implementation
- Files: safety.py, gesture_node.py, tests/test_safety.py.
- Checked: Windows `python -B -m unittest discover -s tests -v`: 5 passed.
- Behavior: 5-frame debounce; two fists immediately emit emergency; invalid/missing
  input emits hold at 2 s and land at 5 s total. Parameters configure these defaults.
  Camera read failures count as missing input; two-hand recognition enabled.
- Untested: ROS parameter wiring, camera/MediaPipe, runtime timing and SITL.

## 2026-11-08 Task 2: bridge safety commands
- Files: flight_logic.py, flight_cmd_bridge.py, tests/test_flight_logic.py.
- Checked: Windows unittest suite: 13 passed, including mocked service ordering,
  failure short circuit, arm/land skips, hold, emergency and takeoff cancellation.
- Behavior: hold selects LOITER (no GUIDED fallback without a position target);
  emergency/land use land service, with known-disarmed skip. Unknown/disconnected
  state blocks takeoff; unknown state does not suppress landing. Safety commands
  invalidate remaining takeoff steps; concurrent duplicate sequences are skipped.
- Props-off warning: remove propellers and disconnect motor power for bench work;
  this is not authorization to arm. Integration tests are SITL only.
- Untested: ROS/MAVROS, mode acceptance, actual altitude, hardware. Already sent
  service requests cannot be recalled; safety command delivery is not guaranteed.

## 2026-11-08 Task 3: keyboard teleop
- Files: teleop_logic.py, keyboard_teleop.py, setup.py, tests/test_teleop.py.
- Checked: Windows unittest suite: 15 passed. Mapping and unknown-key behavior tested.
- Behavior: t takeoff, l land, h hold, space emergency land; q exits. Explicit
  terminal input only. Exit/terminal loss does not automatically issue a command.
- Untested: Linux terminal restoration and ROS publishing; no hardware tests.

## 2026-11-08 Task 4: Quest static HUD
- Files: quest/index.html, docs/QUEST_HUD.md.
- Checked: inspected static HTML/JS: image-only transport, explicit stream URL,
  fullscreen handling, no command publisher or flight controls, no build step.
- Untested: Quest browser, WebXR, stream/camera and actual latency. Layout is
  WebXR-ready design groundwork, not an immersive session. Deadman is notes only.

## 2026-11-08 Task 5: board validation and final checks
- Files: docs/SAFETY.md, docs/TESTING_ON_BOARD.md; compatibility correction in
  flight_logic.py preserves takeoff(2.0m)=OK and land=OK acknowledgement text
  consumed by the existing SITL integration script; tests/test_classifier.py
  adds six synthetic finger-count cases.
- Checked: `python -B -m unittest discover -s tests -v`: 16 tests passed
  (classifier test includes six subcases). AST parsing passed for all 22 Python
  source/test files. quest/index.html parsed using HTMLParser; manually reviewed
  JS and absence of flight transport. No git commands executed; network untouched.
- `python -B -m pytest tests -q -p no:cacheprovider` could not run because pytest
  is not installed. All new tests run under standard-library unittest instead.
- Docs give board-only git pull --ff-only, python3 -m colcon build/test,
  simulator isolation/startup, legacy integration test, new-command manual checks,
  camera-only and keyboard-only checks. These commands were not executed here.
- Untested: ROS/ament lint, Linux terminal, MediaPipe/camera, MAVROS/SITL,
  flight/FC behavior, Quest rendering/fullscreen, stream freshness and WebXR.
  No hardware was armed; no flight or network configuration changed outside the
  explicitly documented command/debounce/failsafe behavior.

## Autonomous backlog 1: Landing platform concept and phases
- Files: docs/LANDING_PLATFORM.md.
- Validation: full Windows unittest suite passed. ['Ran 16 tests in 0.002s', '', 'OK']
- Limits/behavior: Offline only; ROS, SITL and hardware untested.

## Autonomous backlog 2: Precision landing state machine
- Files: src/gesture_control/gesture_control/landing.py, tests/test_landing.py.
- Validation: full Windows unittest suite passed. ['Ran 18 tests in 0.002s', '', 'OK']
- Limits/behavior: New OFFLINE landing proposal only: 0.2 m/s lateral, 0.08 m alignment, 0.15/0.04 m/s descent; lost acquired pose aborts; contact required. Camera extrinsics, detector, ROS, SITL and hardware untested.

## Autonomous backlog 3: Rover controller and watchdog
- Files: src/gesture_control/gesture_control/rover.py, tests/test_rover.py.
- Validation: full Windows unittest suite passed. ['Ran 20 tests in 0.002s', '', 'OK']
- Limits/behavior: Offline: 0.4 m/s wheel cap, 0.2 m/s forward cap, 0.5 s watchdog. No localization, obstacle sensing, motor driver or hardware validation.

## Autonomous backlog 4: Versioned rover protocol
- Files: src/gesture_control/gesture_control/protocol.py, tests/test_protocol.py, docs/PROTOCOL.md.
- Validation: full Windows unittest suite passed. ['Ran 22 tests in 0.007s', '', 'OK']
- Limits/behavior: Offline only; ROS, SITL and hardware untested.

## Autonomous backlog 5: Rover firmware skeleton
- Files: firmware/rover_micropython.py.
- Validation: full Windows unittest suite passed. ['Ran 22 tests in 0.002s', '', 'OK']
- Limits/behavior: Skeleton only, deliberately disabled motor output; no MicroPython, serial, driver or hardware testing. Protocol decoder injected.

## Autonomous backlog 6: Randomized landing simulator
- Files: src/gesture_control/gesture_control/simulation.py, tools/simulate_landings.py, tests/test_simulation.py.
- Validation: full Windows unittest suite passed. ['Ran 23 tests in 0.023s', '', 'OK']
- Limits/behavior: Toy constant-speed rover plus wind; no aerodynamics, latency, tag loss or collision model. No real success-rate claim.

## Autonomous backlog 7: Geofence and battery RTL policy
- Files: src/gesture_control/gesture_control/geofence.py, tests/test_geofence.py.
- Validation: full Windows unittest suite passed. ['Ran 24 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline advisory defaults 20 m radius/5 m ceiling/25% RTL; no bridge wiring. Requires valid home, localization and RTL capability; SITL untested.

## Autonomous backlog 7: Geofence and battery RTL policy
- Files: src/gesture_control/gesture_control/geofence.py, tests/test_geofence.py.
- Validation: full Windows unittest suite passed. ['Ran 25 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline advisory defaults 20 m radius/5 m ceiling/25% RTL; no bridge wiring. Requires valid home, localization and RTL capability; SITL untested.

## Autonomous backlog 8: Battery hysteresis policy
- Files: src/gesture_control/gesture_control/battery.py, tests/test_battery.py.
- Validation: full Windows unittest suite passed. ['Ran 25 tests in 0.023s', '', 'OK']
- Limits/behavior: Offline configurable 3.5/3.3 V per cell and 0.15 V hysteresis. Chemistry, load sag, telemetry and RTL availability unvalidated; no FC changes.

## Autonomous backlog 9: Command arbitration
- Files: src/gesture_control/gesture_control/arbitration.py, tests/test_arbitration.py.
- Validation: full Windows unittest suite passed. ['Ran 26 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline 0.5 s lease, safety-command precedence, keyboard > Quest > gesture > voice. Existing ROS publishers remain unarbitrated; no authentication.

## Autonomous backlog 7: Geofence and battery RTL policy
- Files: src/gesture_control/gesture_control/geofence.py, tests/test_geofence.py.
- Validation: full Windows unittest suite passed. ['Ran 27 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline advisory defaults 20 m radius/5 m ceiling/25% RTL; no bridge wiring. Requires valid home, localization and RTL capability; SITL untested.

## Autonomous backlog 8: Battery hysteresis policy
- Files: src/gesture_control/gesture_control/battery.py, tests/test_battery.py.
- Validation: full Windows unittest suite passed. ['Ran 27 tests in 0.023s', '', 'OK']
- Limits/behavior: Offline configurable 3.5/3.3 V per cell and 0.15 V hysteresis. Chemistry, load sag, telemetry and RTL availability unvalidated; no FC changes.

## Autonomous backlog 9: Command arbitration
- Files: src/gesture_control/gesture_control/arbitration.py, tests/test_arbitration.py.
- Validation: full Windows unittest suite passed. ['Ran 27 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline 0.5 s lease, safety-command precedence, keyboard > Quest > gesture > voice. Existing ROS publishers remain unarbitrated; no authentication.

## Autonomous backlog 10: Quest deadman logic
- Files: src/gesture_control/gesture_control/deadman.py, tests/test_deadman.py.
- Validation: full Windows unittest suite passed. ['Ran 27 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline 250 ms deadman; release/repress on tracking loss. No Quest input transport.

## Autonomous backlog 11: Flight recorder and replay
- Files: src/gesture_control/gesture_control/recording.py, tools/replay_log.py, tests/test_recording.py.
- Validation: full Windows unittest suite passed. ['Ran 29 tests in 0.024s', '', 'OK']
- Limits/behavior: Recorder accepts explicit local events only; caller must keep credentials out of free text. No ROS capture or replay actuation.

## Autonomous backlog 12: Preflight report
- Files: src/gesture_control/gesture_control/preflight.py, tests/test_preflight.py, docs/PREFLIGHT.md.
- Validation: full Windows unittest suite passed. ['Ran 30 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline only; ROS, SITL and hardware untested.

## Autonomous backlog 13: Extended gesture classifier
- Files: src/gesture_control/gesture_control/extended_gestures.py, tests/test_extended_gestures.py.
- Validation: full Windows unittest suite passed. ['Ran 31 tests in 0.023s', '', 'OK']
- Limits/behavior: Opt-in classifier only; legacy classifier and flight mappings unchanged. Synthetic fixtures only, not real accuracy or handedness validation.

## Autonomous backlog 14: Gesture velocity mapping
- Files: src/gesture_control/gesture_control/velocity.py, tests/test_velocity.py.
- Validation: full Windows unittest suite passed. ['Ran 32 tests in 0.023s', '', 'OK']
- Limits/behavior: Offline vector cap 0.2 m/s and normalized 0.1 deadzone; disabled by default; camera/body mapping and setpoint transport absent.

## Autonomous backlog 15: Follow-me PID
- Files: src/gesture_control/gesture_control/follow.py, tests/test_follow.py.
- Validation: full Windows unittest suite passed. ['Ran 34 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline PID output +/-0.2; no obstacle avoidance, target identity or actuation. Gain tuning, dynamics, camera and SITL untested.

## Autonomous backlog 16: Pan-tilt controller
- Files: src/gesture_control/gesture_control/pantilt.py, tests/test_pantilt.py.
- Validation: full Windows unittest suite passed. ['Ran 35 tests in 0.024s', '', 'OK']
- Limits/behavior: Offline 30–150 degree limits, smoothing alpha 0.2. Actual servo range, orientation, power, rate and bracket clearance untested.

## Autonomous backlog 17: Landmark smoothing filters
- Files: src/gesture_control/gesture_control/filters.py, tests/test_filters.py.
- Validation: full Windows unittest suite passed. ['Ran 37 tests in 0.025s', '', 'OK']
- Limits/behavior: Filters offline; not inserted into live recognition; added latency unmeasured.

## Autonomous backlog 18: Dataset recorder and evaluator
- Files: src/gesture_control/gesture_control/dataset.py, tools/evaluate_gestures.py, tests/test_dataset.py.
- Validation: full Windows unittest suite passed. ['Ran 38 tests in 0.025s', '', 'OK']
- Limits/behavior: Explicit landmark sample API; no automatic camera capture. Synthetic tests only, no real dataset or recognition accuracy claim.

## Autonomous backlog 19: Quest telemetry HUD
- Files: quest/index.html, docs/QUEST_TELEMETRY.md.
- Validation: full Windows unittest suite passed. ['Ran 38 tests in 0.025s', '', 'OK']
- Limits/behavior: View-only telemetry display; no input publishing. Browser/Quest/real telemetry untested.

## Autonomous backlog 20: Web dashboard and mock server
- Files: dashboard/index.html, src/gesture_control/gesture_control/mock_server.py, tests/test_mock_server.py, docs/DASHBOARD.md.
- Validation: full Windows unittest suite passed. ['Ran 39 tests in 0.747s', '', 'OK']
- Limits/behavior: Loopback HTTP tested using ephemeral port; dashboard displays mock ack history. Real /flight_cmd_ack adapter and browser/Quest rendering untested.

## Autonomous backlog 21: English and Russian voice parser
- Files: src/gesture_control/gesture_control/voice.py, tests/test_voice.py.
- Validation: full Windows unittest suite passed. ['Ran 40 tests in 0.593s', '', 'OK']
- Limits/behavior: Text parser only; exact phrase required. No audio or ROS command publisher.

## Autonomous backlog 22: dronectl CLI
- Files: src/gesture_control/gesture_control/cli_logic.py, src/gesture_control/gesture_control/dronectl.py, tests/test_cli.py, src/gesture_control/setup.py.
- Validation: full Windows unittest suite passed. ['Ran 41 tests in 0.607s', '', 'OK']
- Limits/behavior: New CLI defaults dry-run; explicit SITL attestation required for publish. Attestation is not hardware detection; ROS delivery/discovery untested.

## Autonomous backlog 23: Package and source quality checks
- Files: tests/test_structure.py, docs/ENGINEERING.md.
- Validation: full Windows unittest suite passed. ['Ran 43 tests in 0.618s', '', 'OK']
- Limits/behavior: AST/import/package checks passed; ament/flake8, colcon install and ROS untested.

## Autonomous backlog 24: Portable test runner and CI
- Files: tests/run_all.py, .github/workflows/tests.yml.
- Validation: full Windows unittest suite passed. ['Ran 43 tests in 0.656s', '', 'OK']
- Limits/behavior: Full Windows unittest passed; workflow written but remote Ubuntu/Windows CI not executed. Live flight integration and ament lint deliberately excluded from portable runner.

## Autonomous backlog 25: English and Russian portfolio README
- Files: README.md, README_RU.md.
- Validation: full Windows unittest suite passed. ['Ran 43 tests in 0.676s', '', 'OK']
- Limits/behavior: Docs checked against current source; target builds, camera recognition and real flight not verified. No hardware claims added.

## Autonomous backlog 26: Architecture documentation
- Files: docs/ARCHITECTURE.md.
- Validation: full Windows unittest suite passed. ['Ran 43 tests in 0.651s', '', 'OK']
- Limits/behavior: Offline only; ROS, SITL and hardware untested.

## Autonomous backlog 27: Phased roadmap
- Files: docs/ROADMAP.md.
- Validation: full Windows unittest suite passed. ['Ran 43 tests in 0.674s', '', 'OK']
- Limits/behavior: Offline only; ROS, SITL and hardware untested.

## Autonomous backlog 28: FAA verification checklist
- Files: docs/LEGAL_FAA.md.
- Validation: full Windows unittest suite passed. ['Ran 43 tests in 0.641s', '', 'OK']
- Limits/behavior: FAA primary sources consulted; individual operation, campus policy and legal eligibility not determined; verify before use.

## Autonomous backlog 29: Portfolio presentation
- Files: docs/PORTFOLIO.md.
- Validation: full Windows unittest suite passed. ['Ran 43 tests in 0.646s', '', 'OK']
- Limits/behavior: Offline only; ROS, SITL and hardware untested.

## Autonomous backlog 30: BOM and parametric CAD
- Files: docs/BOM.md, cad/camera_mount.scad, cad/pan_tilt_bracket.scad, cad/landing_pad_frame.scad.
- Validation: full Windows unittest suite passed. ['Ran 43 tests in 0.646s', '', 'OK']
- Limits/behavior: Concept CAD only; OpenSCAD rendering, structural loads, fit and prices untested.

## Autonomous backlog 31: Monotonic telemetry freshness gate
- Files: src/gesture_control/gesture_control/freshness.py, tests/test_freshness.py.
- Validation: full Windows unittest suite passed. ['Ran 44 tests in 0.636s', '', 'OK']
- Limits/behavior: Offline local-receive freshness only; no remote clock synchronization or ROS state wiring.

## Autonomous backlog 32: Replay-resistant rover receiver session
- Files: src/gesture_control/gesture_control/receiver.py, tests/test_receiver.py.
- Validation: full Windows unittest suite passed. ['Ran 46 tests in 0.614s', '', 'OK']
- Limits/behavior: Offline sequence gate and watchdog; CRC still unauthenticated; firmware not connected.

## Autonomous backlog 33: Explicit camera-to-body rigid transform
- Files: src/gesture_control/gesture_control/frames.py, tests/test_frames.py.
- Validation: full Windows unittest suite passed. ['Ran 47 tests in 0.638s', '', 'OK']
- Limits/behavior: Pure transform helper; measured calibration and detector pose convention absent.

## Autonomous backlog 34: Contact debounce with low-height guard
- Files: src/gesture_control/gesture_control/contact.py, tests/test_contact.py.
- Validation: full Windows unittest suite passed. ['Ran 48 tests in 0.643s', '', 'OK']
- Limits/behavior: Offline 0.3 s dwell / 0.15 m height guard; sensor and landing integration absent.

## Autonomous backlog 35: Vector velocity slew-rate limiter
- Files: src/gesture_control/gesture_control/slew.py, tests/test_slew.py.
- Validation: full Windows unittest suite passed. ['Ran 49 tests in 0.643s', '', 'OK']
- Limits/behavior: Offline 0.3 m/s² acceleration, 0.2 m/s cap; stop bypasses smoothing. No flight wiring.

## Autonomous backlog 36: Read-only component health diagnostics
- Files: src/gesture_control/gesture_control/diagnostics.py, tests/test_diagnostics.py.
- Validation: full Windows unittest suite passed. ['Ran 50 tests in 0.629s', '', 'OK']
- Limits/behavior: Offline health summary; no ROS/process/FC state measurement and no authorization.

## Autonomous backlog 37: Bounded telemetry and ack history
- Files: src/gesture_control/gesture_control/history.py, tests/test_history.py.
- Validation: full Windows unittest suite passed. ['Ran 51 tests in 0.646s', '', 'OK']
- Limits/behavior: Bounded explicit local inputs; no ROS capture; caller must not include secrets in ack text.

## Autonomous backlog 38: Landing pose-loss fault campaign
- Files: src/gesture_control/gesture_control/faults.py, tests/test_faults.py, tools/landing_faults.py.
- Validation: full Windows unittest suite passed. ['Ran 52 tests in 0.655s', '', 'OK']
- Limits/behavior: Proposal-level faults only; no FC response or physics claim.

## Autonomous backlog 39: Strict versioned offline configuration
- Files: src/gesture_control/gesture_control/configuration.py, tests/test_configuration.py.
- Validation: full Windows unittest suite passed. ['Ran 53 tests in 0.641s', '', 'OK']
- Limits/behavior: Offline schema only; existing modules keep explicit constructor defaults. No automatic configuration loading or live FC parameter edits.

## Autonomous backlog 40: Documentation links and interface source checks
- Files: tests/test_documentation.py, docs/OFFLINE_POLICIES.md.
- Validation: full Windows unittest suite passed. ['Ran 55 tests in 0.716s', '', 'OK']
- Limits/behavior: Static HTML/link checks only; browser execution, Quest rendering, live transport untested.

## Autonomous backlog 41: Fail-closed malformed input audit
- Files: src/gesture_control/gesture_control/validation.py, src/gesture_control/gesture_control/landing.py, src/gesture_control/gesture_control/protocol.py, src/gesture_control/gesture_control/extended_gestures.py, src/gesture_control/gesture_control/deadman.py, src/gesture_control/gesture_control/velocity.py, tests/test_malformed_inputs.py.
- Validation: full Windows unittest suite passed. ['Ran 58 tests in 0.630s', '', 'OK']
- Limits/behavior: Offline policies now reject truthy non-booleans and malformed/overflowing pose/protocol input. Live classifier/bridge behavior unchanged; ROS/hardware untested.

## Autonomous backlog 42: Landmark JSONL-to-CSV recorder CLI
- Files: src/gesture_control/gesture_control/dataset_cli.py, tests/test_dataset_cli.py, docs/DATASETS.md.
- Validation: full Windows unittest suite passed. ['Ran 60 tests in 0.653s', '', 'OK']
- Limits/behavior: Conversion and CLI exclusive-open contract tested in memory. Windows sandbox denied tempfile directory access; filesystem integration not validated. No camera/real dataset.

## Final autonomous-run summary (2026-11-08)

- Implemented 30 original backlog deliverables plus 12 Codex ideas; 42 boxes checked. Implementation is offline scaffolding/policies where specified, not integrated autonomous flight.
- Validation: 60 portable unittest tests pass on Windows Python 3.12. Full suite run after every completed task, including documentation tasks; regressions fixed before advancing. Repeated entries for tasks 7?9 reflect retries while fixing later-task regressions.
- Additional checks: both HTML inline scripts pass node --check; HTML IDs/local README links checked; 100 seeded toy landings report 100 successes under the limited constant-rover/wind model; five proposal-level landing fault scenarios pass. These numbers are not real-world performance.
- Untested/blocked validation: ROS/ament/flake8/colcon, Linux terminal, camera/MediaPipe, actual tag pose detection/calibration, MAVROS/SITL, real flight, motor driver/MicroPython, Quest/browser rendering, OpenSCAD render/fit/load strength, remote CI, individual FAA/campus eligibility. Firmware remains disabled; real telemetry adapter is absent.
- Sandbox limitation: tempfile filesystem test denied access; recorder conversion and exclusive-open contract tested in memory instead. An empty sandbox-created directory `<repo>/tmp2p5s1_t6` could not be removed (access denied). A first empty temp attempt outside the checkout was likewise denied at `<tmp>/tmpbyf8de7k`; no dataset was written to either.
- Rules: no git commands; .git untouched; network/ not read or modified; no real motors armed or flight/network scripts run. No credentials introduced. New CLI explicit send path is untested and SITL-only; no live policy wiring.
- Safety documentation now identifies experimental modules explicitly. Temporary task-construction scripts are removed at handoff.

### Working-tree file inventory

- `.github/workflows/tests.yml`
- `README.md`
- `README_RU.md`
- `cad/camera_mount.scad`
- `cad/landing_pad_frame.scad`
- `cad/pan_tilt_bracket.scad`
- `dashboard/index.html`
- `docs/ARCHITECTURE.md`
- `docs/BACKLOG.md`
- `docs/BOM.md`
- `docs/DASHBOARD.md`
- `docs/DATASETS.md`
- `docs/ENGINEERING.md`
- `docs/LANDING_PLATFORM.md`
- `docs/LEGAL_FAA.md`
- `docs/NIGHT_LOG.md`
- `docs/OFFLINE_POLICIES.md`
- `docs/PORTFOLIO.md`
- `docs/PREFLIGHT.md`
- `docs/PROTOCOL.md`
- `docs/QUEST_TELEMETRY.md`
- `docs/ROADMAP.md`
- `docs/SAFETY.md`
- `firmware/rover_micropython.py`
- `quest/index.html`
- `src/gesture_control/gesture_control/arbitration.py`
- `src/gesture_control/gesture_control/battery.py`
- `src/gesture_control/gesture_control/cli_logic.py`
- `src/gesture_control/gesture_control/configuration.py`
- `src/gesture_control/gesture_control/contact.py`
- `src/gesture_control/gesture_control/dataset.py`
- `src/gesture_control/gesture_control/dataset_cli.py`
- `src/gesture_control/gesture_control/deadman.py`
- `src/gesture_control/gesture_control/diagnostics.py`
- `src/gesture_control/gesture_control/dronectl.py`
- `src/gesture_control/gesture_control/extended_gestures.py`
- `src/gesture_control/gesture_control/faults.py`
- `src/gesture_control/gesture_control/filters.py`
- `src/gesture_control/gesture_control/follow.py`
- `src/gesture_control/gesture_control/frames.py`
- `src/gesture_control/gesture_control/freshness.py`
- `src/gesture_control/gesture_control/geofence.py`
- `src/gesture_control/gesture_control/history.py`
- `src/gesture_control/gesture_control/landing.py`
- `src/gesture_control/gesture_control/mock_server.py`
- `src/gesture_control/gesture_control/pantilt.py`
- `src/gesture_control/gesture_control/preflight.py`
- `src/gesture_control/gesture_control/protocol.py`
- `src/gesture_control/gesture_control/receiver.py`
- `src/gesture_control/gesture_control/recording.py`
- `src/gesture_control/gesture_control/rover.py`
- `src/gesture_control/gesture_control/simulation.py`
- `src/gesture_control/gesture_control/slew.py`
- `src/gesture_control/gesture_control/validation.py`
- `src/gesture_control/gesture_control/velocity.py`
- `src/gesture_control/gesture_control/voice.py`
- `src/gesture_control/setup.py`
- `tests/run_all.py`
- `tests/test_arbitration.py`
- `tests/test_battery.py`
- `tests/test_cli.py`
- `tests/test_configuration.py`
- `tests/test_contact.py`
- `tests/test_dataset.py`
- `tests/test_dataset_cli.py`
- `tests/test_deadman.py`
- `tests/test_diagnostics.py`
- `tests/test_documentation.py`
- `tests/test_extended_gestures.py`
- `tests/test_faults.py`
- `tests/test_filters.py`
- `tests/test_follow.py`
- `tests/test_frames.py`
- `tests/test_freshness.py`
- `tests/test_geofence.py`
- `tests/test_history.py`
- `tests/test_landing.py`
- `tests/test_malformed_inputs.py`
- `tests/test_mock_server.py`
- `tests/test_pantilt.py`
- `tests/test_preflight.py`
- `tests/test_protocol.py`
- `tests/test_receiver.py`
- `tests/test_recording.py`
- `tests/test_rover.py`
- `tests/test_simulation.py`
- `tests/test_slew.py`
- `tests/test_structure.py`
- `tests/test_velocity.py`
- `tests/test_voice.py`
- `tools/evaluate_gestures.py`
- `tools/landing_faults.py`
- `tools/replay_log.py`
- `tools/simulate_landings.py`
