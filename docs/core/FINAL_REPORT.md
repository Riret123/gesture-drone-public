# Core flight work report

**Not cleared for physical flight or powered motor testing.** This continuation
implements and tests portable safeguards; actual board/SITL acceptance remains
unfinished. A requested two-hour offline stress campaign is currently running.
Its final result must replace the provisional checkpoint below before handoff.

## Validation and provenance

Latest full Windows invocation: `python -B tools/verify_portable.py`:
**818 unittest cases passed**, process exit 0. A 219-file before/after source
manifest had no endpoint drift; manifest digest:
`ac5922c7ddcefd9824229ee3e751ea55b47de8a2969e58029b081a13be634dbf`.
This is not an immutable snapshot and cannot detect a transient edit restored
between hashes. Stop other writers before target acceptance.

The current tree includes preserved concurrent recovery contributions: strict
doctor state ambiguity rejection, source AST checks, per-row CSV mutation tests,
a 2,000-frame post-latch campaign, additional acceptance/measurement guides and
28 backlog items. Another writer's earlier report arrived during this run.
Ownership clarification was requested; no answer is recorded. Counts describe the
whole observed tree, not exclusive authorship by one session.

The primary continuation added 26 additional red-team tasks and continued several.
A sustained seed-20261109 campaign checks independent latch invariants, random
service failures/state age/reset attempts, rigid image transforms, malformed
landmarks and real-thread service-boundary cancellation. At 300 seconds it had
passed 87,738 cases, 8,773,800 command steps, 350,952 geometry checks and 1,755
thread trials. It checks seven core source hashes each minute. This provisional
checkpoint is not a completed two-hour result and is not ROS/FC/flight evidence.

## Implemented behavior

1. Service discovery and responses retain five-second defaults, bounded at startup
   to 0.1..30 seconds. Three cumulative failures open each independent service/
   mode circuit; one callback per operation/mode may be in flight. Zero automatic
   actuation retries and no half-open arm/takeoff probes. Landing has separate
   circuit capacity. Uncertain timeout does not mean the FC ignored a request.
2. Fist/land/emergency latch inhibition at receipt, including busy admission or
   thread-start failure. Hold cannot replace latched landing. Every live bridge
   launch starts inhibited, so restart cannot bypass the operator reset gate.
   Reset requires an explicit operator_reset command, idle workers and five
   seconds of advancing connected/disarmed receive observations. Samples must be
   <2 seconds old with gaps <2 seconds; cached/pre-latch state cannot accumulate
   dwell. No automatic disarm or altitude change is introduced.
3. Epoch guards recheck after service waits and state reads. Bounded admission
   reserves landing capacity and queues no commands. Already-submitted native/FC
   requests remain uncancellable; no lock is held across external service calls.
4. A 0.2-second bridge timer attempts emergency once per session after a previously
   connected FC is unavailable. It separately watches completed-frame heartbeat
   loss after first accepted health: three seconds default (0.5..10 configurable).
   Same-host heartbeat v1 requires session, advancing sequence, <=0.5-second source
   age and depth-one history. Reset re-enables supervision without renewing old
   health. A broken FC transport cannot deliver landing; bridge/companion death
   still needs independent FC failsafes and pilot authority.
5. COMMAND_STATE_TABLE.md documents 60 generated command cells. Another 240 actual
   adapter primitive cases cover six mode values, connectivity, armed state and
   latch. Thread/race/property and malformed-input tests supplement these finite
   abstractions; arbitrary firmware/executor/thread schedules are not proven.
6. Default classification remains 2D at ratio 1.1. Optional pose_profile_path loads
   bounded versioned JSON bound to requested camera geometry/FPS/mirror policy and
   installed MediaPipe version/model. Deployment confidence margin >=0.5 and angle
   gap >=10 degrees are required. 3D world outputs have no 2D fallback on missing
   or mismatched hands. Negotiated width/height and FPS are checked when enabled.
   Camera back-of-hand/occlusion accuracy remains unmeasured.
7. New capture requests default to 640x480/30 fps/model 0. Returned frame processing
   over 200 ms default contributes missing input. This does not measure exposure
   age or interrupt a native call. Existing five-frame debounce and 2/5-second
   input-loss hold/land defaults remain; takeoff remains GUIDED -> arm -> 2 m.
8. Strict core YAML subset/schema validates types, bounds, duplicates, unknown keys,
   quoted paths and hold-before-land ordering. ROS startup overrides have matching
   numerical bounds. Calibration, benchmark and manifest tools are portable.
9. Landmark CSV replay shares live frame classification and gesture policy, then
   uses the bridge controller and fake MAVROS/FC. Scenarios cover normal commands,
   lost hand, flicker, two fists, duplicate requests and injected RC/battery/link
   faults. Landing ACK intentionally does not disarm the fake FC. RC and battery
   events are explicit harness inputs, not live subscriptions or new FC settings.
10. Board/SITL shell, service/environment and ROS scenario sources were read line
    by line. Fixed camera-only FCU requirement, late component rejection, missing
    environment-file errors and pre-control YAML checks. Doctor uses read-only
    subprocess probes for ROS environment, topic/service names/types, one returned
    connected/disarmed state, serial/camera presence, disk and time sync. Optional
    camera capture runs separately; combined output is capped during capture and
    direct children time out. No live doctor probes were run here.

FIRST_TESTS.md provides staged beginner commands and stop conditions; BRINGUP.md
retains identity/wiring/calibration/failsafe gates. PERFORMANCE.md and
ORANGE_PI_MEASUREMENT.md provide measurement plans. A measured Windows synthetic
pure-classifier run had 400 samples, total p50 0.0701 ms, p95 0.0807 ms, maximum
1.7879 ms. The recorded timing fixture tests accounting only; it excludes camera,
MediaPipe, ROS and FC, and establishes no Orange Pi performance bound.

## Untested and unresolved

No Linux/ARM bootstrap or dependency lock, colcon/ament, Bash/shellcheck/systemd,
real ROS executor, installed MAVROS, real camera/MediaPipe inference, thermal run,
SITL flight physics, RC/battery/GCS failsafe result, physical PCB identity, UART,
motor map/direction, powered motor/tether test or hover was validated.

MAVROS launch now requires explicit fcu_url; there is no default physical serial
selection. Read MAVROS_CONTRACTS.md before target tests: the tagged command backend
can serialize landing behind another command ACK wait. Local reserved worker
capacity is not a guarantee of FC landing priority. Installed package behavior and
applied plugin parameters must be read back and measured, not inferred from YAML.

String commands/reset/heartbeat remain unauthenticated. Flight commands/ACKs lack
session freshness and request IDs; a delayed same-command ACK remains ambiguous.
Heartbeat freshness assumes both processes share one OS monotonic clock domain.
It supervises only after first health and cannot protect a dead bridge/companion.
Already-committed requests may execute after a later safety command. Service
failure circuits may prevent further submissions until reviewed process recovery;
never restart to avoid unresolved vehicle state. Source camera identity uses an
index/configuration convention, not physical sensor attestation. Thumb articulation
and real landmark occlusion remain unresolved.

Doctor state parsing is a restricted known-state document subset, not a general
YAML parser or source timestamp guarantee. Topic/type presence does not prove
publisher authority or health. Direct-child timeout is not validated Linux
process-group/descendant cleanup. Powered test parameters, tether ratings and
aircraft-specific hover limits cannot be supplied without verified hardware and a
qualified human test lead.

## Exact human steps on the board

1. Keep all props removed and motor/ESC power disconnected. Stop duplicate source
   writers. Resolve PCB revision/firmware target, connector pinout, UART voltage/
   baud and supply/backfeed design using BRINGUP.md. Save firmware/parameter
   evidence privately. Do not guess a target or copy generic FC parameters.
2. Transfer the reviewed working tree, excluding environments/logs/data. The example
   workspace below is historical; replace it with the confirmed deployment root.
   Establish compatible Linux ARM dependencies with mp.solutions.hands, then in
   each required terminal:

   ```bash
   cd ~/jedi_drone_ws
   source /opt/ros/jazzy/setup.bash
   source ai_env/bin/activate
   python3 -B tools/check_core_config.py config/core.yaml
   python3 -B tools/verify_portable.py
   python3 -m colcon build
   source install/setup.bash
   python3 -m colcon test
   python3 -m colcon test-result --verbose
   python3 -B tools/doctor.py --plan
   ```

   Stop on failure, wrong interpreter/import version or source drift. Record exact
   working OS/Python/OpenCV/MediaPipe/ROS/MAVROS versions; none is board-verified here.
3. With bridge stopped and motor power disconnected, follow FIRST_TESTS.md camera
   observation in two sourced terminals: `ros2 topic echo /flight_cmd`, then
   `ros2 run gesture_control gesture_node --ros-args --params-file config/core.yaml`.
   Stop gesture before preview/video/doctor camera capture. Test both hand sides,
   occlusion, absent/mixed hands, two fists and slow/failure paths. Retain labeled
   evidence outside source. Do not activate a saved profile before held-out tests.
4. Review BOARD_SERVICES.md and scripts on Linux with `bash -n` and available
   shellcheck before manual use. Replace template paths; keep DRONE_MODE=observe.
   Do not enable boot services or automatic restart. For optional exclusive camera
   probe use `python3 -B tools/doctor.py --probe-camera`; topic/FC checks can fail
   until observation components exist. Never start a physical bridge to make the
   diagnostic green.
5. For isolated SITL only, physically isolate real FCs and other ROS participants,
   use one dedicated ROS domain, stop camera/keyboard publishers and follow
   SITL.md to start external simulator/MAVROS at udp://:14550@ and bridge with the
   reviewed config. Observe connected/disarmed state for at least five seconds,
   then explicitly confirm and require its matching OK ACK:

   ```bash
   ros2 topic pub --once /flight_cmd std_msgs/msg/String '{data: operator_reset}'
   python3 -B tools/sitl_ros_scenarios.py takeoff
   python3 -B tools/sitl_ros_scenarios.py takeoff --execute --sitl-isolated \
     --fcu-url 'udp://:14550@'
   ```

   The one-shot reset publisher must exit before the runner checks publisher
   count. Repeat observed dwell/reset before each later scenario after landing.
   Run hold/land/emergency separately; RC loss additionally requires explicit
   --allow-rc-fault and reviewed expected mode. Check SIM_RC_FAIL restores to zero.
   Stop on uncertain ACK, altitude, mode, touchdown, isolation or fault restoration.
6. In isolated SITL, independently test gesture native stall/process death after
   first heartbeat, FC link loss, bridge death with MAVROS alive, mode/service
   rejection, source reconnect, stale state and reset races. Measure actual
   time-to-FC-action and altitude/landed behavior; mocked ACKs do not prove them.
7. On the actual Orange Pi with motor power disconnected and bridge stopped,
   follow PERFORMANCE.md for negotiated camera, CPU/thermal/contention, exposure/
   buffering and latency/error measurements. Changing FPS changes debounce time.
   Do not weaken confidence, debounce or loss thresholds to improve a demo.
8. Complete a separately approved qualified-human props-off motor-map/direction
   campaign, engineering review for any powered tether, and pilot-only hover
   before any gesture flight campaign. FIRST_TESTS.md links official procedures
   and lists stop conditions. No motor command was executed or supplied by this
   agent; unknown hardware prevents a defensible universal throttle/tether recipe.

## Workspace hygiene

No git commands or network/ access, secrets, service installation,
physical motor arming or live flight commands were performed. Read-only web
references were consulted for documentation. Five empty failed-test directories
remain after automatic approval review rejected cleanup:
tmp4i8g6gq4, tmp7mchoq_a, tmpm8pzw6qn, tmpy8718hcq, tmpyflz_vp1.
The older tmp2p5s1_t6 was not touched. LOG.md records the Windows permission issue.
All intended work remains in the working tree for human review/commit.
