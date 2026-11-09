# Installed MAVROS contract review

This is a source review, not an installed-ROS test. Historical notes mention
MAVROS 2.14.0; confirm the actual version and package contents on the board.
Do not substitute a current upstream branch for target evidence.

In tagged 2.14.0 command.cpp, arm/takeoff/land services share a mutually-exclusive
callback group and the default command ACK wait is five seconds. Therefore a
reserved Python landing worker does not imply immediate MAVROS/FC landing
submission while another command callback is waiting. Measure that delay in
isolated SITL; independent FC failsafes remain essential. The reviewed send path
submits the command and waits for ACK, but does not establish cancellation of a
late FC action. [MAVROS 2.14.0 command plugin source](https://raw.githubusercontent.com/mavlink/mavros/2.14.0/mavros/src/plugins/command.cpp)

The companion's five-second response timeout can race the backend's own wait.
An uncertain timeout must not cause a blind retry or disabled checks. Bridge-level
retry/circuit limits are not a certified bound on every transport/firmware layer.
No installed MAVROS timeout, callback group or FC parameter was changed here.

Tagged 2.14.0 param.cpp exposes GetParameters and ParamSetV2; its getter returns
cached parameter values. Cache presence/zero value is an extra refusal gate, not
physical simulator identity or a fresh FC read. The runner uses force_set=false
and permits only explicit SIM_RC_FAIL 0/1 mutation for isolated RC-loss tests.
[MAVROS 2.14.0 parameter plugin source](https://raw.githubusercontent.com/mavlink/mavros/2.14.0/mavros/src/plugins/param.cpp)

An upstream report documents a 2.15 plugin-subnode parameter-file regression and
links its fix. Inspect the installed version/patch and read back intended values;
do not assume loading a YAML file means every plugin applied it. This report does
not establish whether the board's binary is affected. [Upstream issue and fix record](https://github.com/mavlink/mavros/issues/2294)

With motor power disconnected and control nodes stopped, these commands only
inspect installed types/parameters. First source the real ROS/workspace environment:

```bash
ros2 pkg prefix mavros
ros2 node list
ros2 service type /mavros/cmd/arming
ros2 service type /mavros/cmd/takeoff
ros2 service type /mavros/cmd/land
ros2 service type /mavros/param/get_parameters
ros2 service type /mavros/param/set
ros2 param get /mavros/cmd command_ack_timeout
python3 -B tools/doctor.py --plan
```

If node names differ, identify their namespace from the actual graph before
inspection; do not remap into a guessed FC. Record package version separately
using the board's package manager and installed package.xml. Expected service
types are CommandBool, CommandTOL, CommandTOL, GetParameters and ParamSetV2 in
their matching ROS namespaces. Wrong/missing types, unapplied configuration,
unknown cached parameter state or uncertain isolation are stop conditions.

In isolated SITL, measure arm/takeoff ACK stalls versus landing request time,
service timeout versus actual FC action, duplicate ACKs, rejected mode, FC
disconnect/reconnect and bridge death while MAVROS heartbeats persist. Retain
receive/submit/ACK/FC-observed timestamps and raw FC event logs outside source.
Do not interpret Python worker admission or mock acceptance as physical priority.

Tagged sys_status.cpp publishes State when a target HEARTBEAT is processed.
That supports advancing observations in principle, but does not establish the
installed FC heartbeat rate, delivery jitter or queued-source freshness. Measure
the actual stream with `timeout 15 ros2 topic hz /mavros/state` in observation
mode; the timeout ending this read-only measurement is intentional. The reset
gate requires receive gaps below two seconds. [MAVROS 2.14.0 state publication source](https://raw.githubusercontent.com/mavlink/mavros/2.14.0/mavros/src/plugins/sys_status.cpp)

Official Jazzy rclpy client source exposes remove_pending_request for releasing
local pending-response correlation. It does not cancel a delivered FC command.
Its availability wait polls rather than providing a hard real-time deadline;
Python/native scheduling and client locks must be measured on the target.
[rclpy Jazzy client source](https://raw.githubusercontent.com/ros2/rclpy/jazzy/rclpy/rclpy/client.py)
