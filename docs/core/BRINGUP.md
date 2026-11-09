# Board bring-up and human acceptance record

This is a staged verification procedure, not a verified wiring diagram. No board
is connected to this Windows checkout. Keep motor power disconnected and props
removed during inspection. This run never arms real motors. Any later powered
motor test or flight is a separate human-operated campaign with its own approval.

Launch now requires an explicit fcu_url; it no longer supplies a physical serial
placeholder by default. Confirm the endpoint before every manual observation run.

## Identity and firmware gate

Photograph top/bottom PCB markings, revision, connectors and sensor chips. Record
seller part number and obtain the manufacturer's matching pinout. AERO SELFIE,
H743 and FMUv5 labels alone do not establish an ArduPilot target. FMUv5 is not a
substitute for identifying the PCB. Do not flash on the strength of a product name.

Compare installed firmware's board ID, version and target with the release's
hardware definition and manufacturer record. Save existing parameter export and
firmware details first. MicoAir has distinct original, v2 and AIO products:
[original manual](https://micoair.com/en/docs/flight-controller/micoair743/micoair743-flight-controller-manual),
[v2 manual](https://micoair.com/en/docs/flight-controller/micoair743/micoair743v2-flight-controller-manual).
The manufacturer lists MicoAir743v2 as the v2 ArduPilot target on its
[v2 product page](https://micoair.com/flightcontroller_micoair743v2/).
This does not prove the AERO SELFIE board is that model. Resolve discrepancies
before firmware installation. Record the exact selected release and image hash.

Use `python -B tools/check_firmware_artifact.py PATH_TO_IMAGE.apj
--expected-board-id VERIFIED_ID --expected-sha256 TRUSTED_RELEASE_HASH` as a
read-only local artifact check (one line in the shell). Obtain VERIFIED_ID from
the exact release hardware definition/bootloader record, not from the marketing
label. The tool checks APJ identity, bounded decompression, declared image size
and optional trusted artifact hash; it never flashes or downloads. Its reported
hashes do not establish authenticity without a separately trusted reference, and
it does not verify signatures or physical PCB identity. APJ format reference:
[ArduPilot make_apj](https://raw.githubusercontent.com/ArduPilot/ardupilot/master/Tools/scripts/make_apj.py).

## UART and receiver gate

Map each physical connector to MCU UART and ArduPilot logical SERIAL index from
the exact firmware revision. ArduPilot numbering is logical, documented in
[serial configuration](https://ardupilot.org/copter/docs/common-serial-options.html).
For the original target only, the current
[MicoAir743 hardware definition](https://github.com/ArduPilot/ardupilot/blob/master/libraries/AP_HAL_ChibiOS/hwdef/MicoAir743/hwdef.dat)
orders USB, USART1, USART2, USART3, UART4, USART6, UART7, UART8 as SERIAL0..7.
That reference is mutable: verify the installed release and PCB, rather than
assuming a UART label equals a SERIAL index.

Record a completed table locally before wiring:

| Function | PCB connector/pins | MCU UART | SERIAL index | Protocol | Baud |
| --- | --- | --- | --- | --- | --- |
| Companion | unverified | unverified | x, unverified | MAVLink2 (2) | matched pair |
| ELRS receiver | unverified | unverified | y, distinct | RC input per firmware | protocol managed |
| GPS | unverified | unverified | unverified | installed GPS protocol | verified |

With power off, verify signal voltage compatibility and common ground; cross TX
to RX. Do not put supply voltage on signal pins. Do not connect two power sources
without a reviewed power design. Confirm Orange Pi UART device/pinmux using its
actual OS image and board documentation. Do not guess /dev/ttySx.

For the confirmed companion port, SERIALx_PROTOCOL=2 selects MAVLink2. Baud
must match both ends; existing 921600 is a placeholder, not a measured choice.
Set matching SERIALx_BAUD using installed firmware's parameter metadata (the
encoded value for 921600 is typically 921). Export/read back and reboot if
required. Do not overwrite the receiver or GPS port. MAVROS target IDs must match
the intended FC; leave GCS forwarding empty until separately reviewed.

For conventional CRSF ELRS, follow
[ArduPilot's receiver setup](https://docs.ardupilot.org/copter/docs/common-tbs-rc.html)
for the installed release; confirm RC-input serial protocol and RC_PROTOCOLS/
RC_OPTIONS rather than reusing MAVLink companion parameters. Receiver variants
can output other protocols; identify configured output first. CRSF uses both TX
and RX for bidirectional operation. Verify channels in the GCS with motor power off.

Bind using the exact receiver/transmitter firmware versions and compatible
frequency/regulatory domain. Follow [ExpressLRS binding](https://www.expresslrs.org/quick-start/binding/):
choose either a privately managed binding phrase or the version's traditional
binding procedure. Never put the phrase in this repository or logs. Traditional
binding requires no receiver binding phrase. Confirm correct model selection,
link status, channel mapping, endpoints, neutral values and deliberate transmitter
loss indication. Binding alone is not calibration or failsafe validation.

## Calibration and actuator review

Using the matching firmware's GCS setup pages, record board orientation first;
then level/accelerometer calibration on a stable surface, compass calibration and
orientation away from magnetic interference, radio endpoints/mapping, flight-mode
switch and battery voltage/current calibration against independent measurements.
Check GPS/EKF health and home position. Keep pre-arm checks enabled; resolve every
failure. Record FRAME_CLASS/FRAME_TYPE and output functions; ESC protocol and
calibration depend on the actual ESC, and DShot must not receive a generic PWM
calibration recipe.

Prepare a motor mapping sheet from the exact frame diagram in
[ArduPilot motor ordering](https://ardupilot.org/copter/docs/connect-escs-and-motors.html).
Include output number, motor-test letter, physical location, expected and observed
direction. Motor-test letters and motor numbers are different labels. Physical
spin/direction verification is **pending separate human powered-test approval**;
it cannot be established with motor power disconnected. When separately approved,
an experienced operator uses the official GCS Motor Test procedure with all props
removed, restrained frame, clear bench and immediate power isolation. This run
provides no automated motor-test script or arming command. Do not infer correct
direction from wire colors, a boot tone or an unpowered inspection.

## FC failsafe acceptance

Capture current values, proposed values, rationale, firmware-specific enum labels
and observed SITL outcome. No parameter import file is supplied: battery chemistry,
capacity, position source and operation area are unknown. Keep an independent
pilot recovery path. Never disable checks to make a test pass.

| Failure | Review parameters | Required evidence |
| --- | --- | --- |
| RC loss | FS_THR_ENABLE, FS_THR_VALUE, FS_OPTIONS; receiver loss signaling | SITL loss in GUIDED and pilot mode; verify intended action and recovery |
| Battery low/critical | BATT_MONITOR, BATT_CAPACITY, BATT_LOW_VOLT/MAH, BATT_CRT_VOLT/MAH, BATT_FS_LOW_ACT, BATT_FS_CRT_ACT, BATT_LOW_TIMER | calibrated readings, pack-specific thresholds; simulated low then critical actions |
| GCS/companion heartbeat loss | FS_GCS_ENABLE, FS_GCS_TIMEOUT, FS_OPTIONS; applicable MAV GCS system-ID parameters | identify monitored heartbeat source; stop that source and measure actual transition |

Use [RC failsafe](https://ardupilot.org/copter/docs/radio-failsafe.html),
[battery failsafe](https://ardupilot.org/copter/docs/failsafe-battery.html) and
[GCS failsafe](https://ardupilot.org/copter/docs/gcs-failsafe.html) for behavior,
then verify names/enum values against the installed release. FS_OPTIONS can alter
actions. Do not choose permissive continuation bits without a reviewed reason.
Battery low/critical thresholds require pack measurements and calibrated monitor;
generic voltages copied from another aircraft are not acceptance evidence.
GCS loss is not necessarily gesture-node loss: MAVROS may keep heartbeats alive
after the camera or bridge dies. Test camera stalls and process deaths separately.
The bridge watchdog only rejects old state; it does not land on bridge failure.

## SITL to first-hover gate

Complete docs/core/SITL.md before considering a hardware campaign. Require
recorded firmware/configuration, expected/observed modes, altitude trace, landed
and disarmed state, service failures, telemetry loss and pilot recovery. Unit
tests check logic and service acceptance; they do not check actual climb/landing.

For a separately approved first flight: qualified pilot and spotter, legal/site
permission, clear exclusion area, measured battery margin, verified frame and
motor map, correct prop installation only at flight site, healthy estimator and
position source, known home, manual recovery mode, independent RC link and
verified FC failsafes. Start with pilot-controlled basic hover and landing;
gesture takeoff waits for a later reviewed campaign. Abort on abnormal attitude,
vibration, voltage sag, position drift, control latency or loss of observer contact.
Do not run the live integration script against the physical FC.

Tether testing is not automatically safer: a tether can entangle props, destabilize
the aircraft or cause aggressive controller corrections. Begin with a nonpowered
geometry/clearance exercise. Any powered rig requires a separately engineered
fixture, rated anchors, entanglement prevention, load analysis, exclusion zone,
remote power isolation and qualified test lead. No free tether or improvised
indoor hover is authorized by this plan. Record test-specific abort limits before
execution; this repository does not supply validated loads or tether dimensions.
