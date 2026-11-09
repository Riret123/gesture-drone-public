# Beginner bench-to-hover checklist

This procedure separates inspection from future powered human tests. No command
here arms physical motors. The identity, wiring, calibration and failsafe gates
in BRINGUP.md must be resolved before a qualified test lead approves powered work.
Propeller removal alone does not authorize arming. Never run the integration or
scenario flight scripts against a physical aircraft.

## 1. First unpowered bench inspection

Remove propellers, disconnect motor/ESC power, and photograph PCB markings and
connectors. Keep the aircraft stable. Confirm the selected USB/companion supply
cannot backfeed motor power. Stop if the power design, voltage compatibility,
board target, UART connector or motor map is unknown. Do not guess pin numbers.

Use the actual transferred workspace; the following path is the documented example:

```bash
cd ~/jedi_drone_ws
source /opt/ros/jazzy/setup.bash
source ai_env/bin/activate
python3 -B tests/run_all.py
python3 -B tools/check_core_config.py
python3 -m colcon build
source install/setup.bash
python3 -m colcon test
python3 -m colcon test-result --verbose
python3 -B tools/doctor.py --plan
```

Stop if any test/build/config check fails or the imported environment differs
from the recorded deployment. No working dependency lock for Linux ARM is supplied.
Record exact OS, Python, OpenCV, MediaPipe, ROS/MAVROS and firmware versions locally.

## 2. Camera-only check

Keep the bridge and all other camera clients stopped. In one sourced terminal:

```bash
ros2 topic echo /flight_cmd
```

In a second equally sourced terminal:

```bash
ros2 run gesture_control gesture_node --ros-args --params-file config/core.yaml
```

Observe open palm, fist, absent hand, conflicting hands and two fists. Commands
are emitted only when output changes. Stop the node with Ctrl-C before using
preview/video/doctor capture. Stop if false open palm appears, gestures vary with
orientation, input-loss behavior is wrong, or camera ownership is unclear.

With gesture/video stopped, this read-only diagnostic optionally opens camera 0
in an eight-second-bounded child, saves no image, and never invokes FC services:

```bash
python3 -B tools/doctor.py --probe-camera
```

Missing ROS topics/FC state can make doctor fail at this camera-only stage; that
is expected until observation components are started. Investigate each result,
not just the exit status. Do not start the physical bridge to turn a diagnostic
green. For physical FC observation use the verified endpoint manually, with motor
power disconnected and the control nodes stopped. See BOARD_SERVICES.md.

## 3. Isolated simulation

Physically isolate all real FCs and other ROS participants. Start external SITL,
MAVROS at `udp://:14550@`, and the bridge as described in SITL.md. Keep camera and
keyboard publishers stopped. Print each scenario before its explicit guarded run.
Observe actual altitude, mode, touchdown/disarm and fault restoration. Stop if
the endpoint, ROS domain, publisher count or simulator identity is uncertain.

Every bridge startup and every landing inhibit takeoff. Only in isolated SITL, observe
connected/disarmed state continuously for at least five seconds, then confirm:

```bash
ros2 topic pub --once /flight_cmd std_msgs/msg/String '{data: operator_reset}'
```

Read the matching ACK; failed reset is a stop condition. A returning heartbeat
does not reset the latch. Do not restart the process to bypass it. This string
command is unauthenticated, so use one trusted publisher and an isolated ROS graph.

## 4. Separate props-off motor campaign

This step is pending human powered-test approval and exact hardware/frame/ESC
identification. Finish the output-number, motor-test-letter, physical-location
and direction sheet first. A qualified lead establishes restraint, clear bench,
short duration, lowest effective test setting, independent observer and immediate
power isolation for the specific motor/ESC. There is no universal safe percentage
or duration for the unknown hardware in this checkout.

The official GUI procedure is Mission Planner **SETUP → Optional Hardware → Motor
Test**. Motor-test letters differ from output/motor numbering. Follow the matching
frame diagram and verify each selected motor/direction individually; do not run
this repository's flight scripts for a motor test. [ArduPilot motor ordering and test](https://ardupilot.org/copter/docs/connect-escs-and-motors.html)

Stop and isolate power on wrong motor, wrong direction, unexpected motion,
overheating, damaged wires, unstable restraint, unexpected arming, or loss of
observer/power-isolation contact. Correct the map and repeat inspection before
any next powered action. Record actual observations; a boot tone is not a test.

## 5. Tether preparation

Perform only a nonpowered clearance exercise until a reviewed fixture exists.
With props removed and motor power disconnected, check every intended attitude,
line route, connector load, anchor and emergency-access path. Stop on any possible
prop/line contact, sharp edge, connector tension or uncertain load path.

A powered tether test requires a qualified engineered load/entanglement/control
interaction review, rated equipment, test-specific abort limits and a test lead.
An improvised rope or indoor lift is not an accepted intermediate step. No
validated tether geometry or load rating is available for this aircraft.

## 6. First hover, later human campaign

Require successful isolated SITL evidence, verified powered motor map/direction,
complete calibration, independent RC authority, measured battery monitor and FC
failsafes, suitable site/exclusion area and qualified pilot/spotter. Keep gesture
control disabled. The pilot reviews the installed firmware's preflight checks,
initial-flight procedure and recovery plan before choosing mode/height/duration.
Do not disable pre-arm checks. [ArduPilot first-flight guide](https://ardupilot.org/copter/docs/flying-arducopter.html)

Stop on abnormal attitude, vibration, drift, voltage sag, estimator warnings,
latency, unexpected mode or loss of pilot/spotter contact. Land using the pilot's
reviewed procedure and retain logs. Gesture flight waits for a later approved
campaign; passing unit tests does not authorize it.
