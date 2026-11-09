# SITL scenario acceptance

`python -B tools/sitl_ros_scenarios.py takeoff` prints a plan without importing
ROS or sending commands. Choices: takeoff, hold, land, emergency, rc-loss. The
Bash wrapper scripts/sitl/scenario.sh forwards arguments and remains plan-only
by default. tools/core_scenarios.py --mock-contract uses an inert acceptance
stub, with no simulator or flight dynamics.

The live ROS adapter is implemented but **not executed or validated on Linux**.
Do not run against any physical aircraft. Before explicitly executing, physically
isolate FCs and other participants, use one dedicated ROS domain, stop gesture/
keyboard/other publishers, inspect actual MAVROS routing and target IDs, and start
external SITL/MAVROS/bridge per AGENTS.md. Endpoint flags attest routing; they do
not reconfigure MAVROS or prove isolation. Confirm initial connected/disarmed/on-
ground state, relative altitude near zero and healthy estimator.

The live bridge now starts inhibited on every process launch. Keep other command
publishers stopped. Observe connected/disarmed state continuously for at least
five seconds, then explicitly confirm startup reset in this isolated simulator:

```bash
ros2 topic pub --once /flight_cmd std_msgs/msg/String '{data: operator_reset}'
```

Require `operator_reset:OK:` on /flight_cmd_ack. The one-shot publisher must have
exited before the scenario runner's one-publisher check. Repeat this observed
dwell and explicit reset before another scenario after landing. Do not restart
the bridge to bypass inhibition. Watchdog loss after first camera heartbeat can
relatch it; keep the camera stopped for these direct-command scenarios.

Run only after reviewing the adapter and installed ROS interfaces:

```bash
python3 tools/sitl_ros_scenarios.py takeoff --execute --sitl-isolated \
  --fcu-url 'udp://:14550@'
```

Repeat separately for hold, land and emergency after confirmed reset/disarm.
RC-loss additionally requires --allow-rc-fault and --rc-mode LAND (or the exact
reviewed expected RTL/SMART_RTL action). Configure the installed firmware's RC
failsafe beforehand; this script never disables checks or edits failsafe settings.
The script requires the cached simulator-only SIM_RC_FAIL parameter to exist and
be zero before commands. This extra gate is still not physical hardware detection.

The runner uses /mavros/param/get_parameters (GetParameters) and /mavros/param/set
(ParamSetV2, force_set=false). Confirm those installed interfaces/names before use.
It changes only SIM_RC_FAIL to 1 for the explicit RC-loss scenario, then attempts
restoration to 0 even after an uncertain timeout or interrupted scenario. Failed
restoration returns failure and requires manual simulator recovery. See official
[ArduPilot simulator parameters](https://docs.ardupilot.org/dev/docs/SITL_simulation_parameters.html)
and [MAVROS ParamSetV2](https://raw.githubusercontent.com/mavlink/mavros/ros2/mavros_msgs/srv/ParamSetV2.srv).
SIM_RC_FAIL=1 is documented as simulated complete RC loss; firmware and simulator
input backends must still be verified to produce the intended failure.

The adapter subscribes to state, extended_state, global_position/rel_alt and
local_position/pose. It requires one command publisher and subscriber, sends once,
matches the command ACK (45 s default sequence budget), and observes outcomes
rather than assuming a service success means flight completed. On any failure it
stops advancing, restores an attempted RC fault and requests manual SITL recovery.
It does not blindly retry takeoff or auto-disarm. Emergency requests landing.

Pure observation acceptance defaults are test tolerances, not flight-control
parameters: max receive age 2 s, target 2 m, altitude tolerance .25 m, position
excursion .3 m, hold dwell 2 s and at least three distinct position samples.
These are provisional and need simulator review before acceptance use. No mode,
altitude or FC parameter is changed to satisfy a test.

| Condition | Required fresh observation |
| --- | --- |
| connected_disarmed | connected, disarmed, ON_GROUND, relative altitude within .25 m of zero |
| airborne_at_target | armed, GUIDED, IN_AIR, relative altitude within .25 m of target |
| loiter_stable | armed, LOITER, IN_AIR, altitude tolerance, bounded position excursion for dwell/new samples |
| configured_rc_failsafe | acknowledged injection marked; a later FC state has the explicitly expected mode |
| landed_disarmed | disarmed, ON_GROUND and relative altitude near zero |

Mode after injection is evidence of the observed transition, not proof that RC
loss caused it. Retain the FC failsafe event log as independent causal evidence.
A telemetry gap or position-stream gap resets hold dwell; clock reversal revokes
observations. Local receive age does not prove fresh source timestamps. The current
String command/ACK protocol lacks request IDs, so a delayed same-command ACK is a
residual risk even with isolated sequential commands.

Record simulator/firmware versions, config export, speedup=1, actual telemetry
traces, expected/observed mode and abort/recovery outcome. Also test GCS heartbeat
loss, camera loss with MAVROS alive, bridge crash, stale state, mode/service
rejection, delayed ACK and simulator reset separately. Stopping MAVROS is not RC
loss. No real SITL result is claimed by Windows mock tests.

The older test_flight_cmd_bridge.py now requires --sitl-isolated plus explicit
--fcu-url udp://:14550@, one publisher/subscriber and fresh initial state. It fails
fast on uncertain ACKs and cleans up ROS in finally. The duplicate open-palm test
is allowed only after confirmed initial acceptance/armed observation; it is not a
blind retry. It also verifies post-landing latch rejection. It still lacks
altitude/landed outcome checks; prefer the observed-outcome runner above. Its live
main is never run by the portable suite and must never run on physical hardware.
