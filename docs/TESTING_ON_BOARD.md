# Board build and SITL checks

These commands assume the deployment checkout is `~/jedi_drone_ws`, ROS Jazzy,
`ai_env` (system site packages, colcon, OpenCV, MediaPipe solutions API, pyyaml),
and a built external ArduPilot checkout with `ardupilot_env`. Those environments
and external revision are not supplied or verified by this checkout. Substitute
the actual workspace path if different. Read SAFETY.md before proceeding.
Stop running bridge/gesture/teleop processes before updating. Do not run network scripts.

Update and build on the board (git commands are documentation only; not executed
by the Windows editing session):

```bash
cd ~/jedi_drone_ws
git pull --ff-only
source /opt/ros/jazzy/setup.bash
source ai_env/bin/activate
touch ai_env/COLCON_IGNORE ardupilot_env/COLCON_IGNORE ardupilot/COLCON_IGNORE
python3 -B -m unittest discover -s tests -v
python3 -m colcon build --packages-select gesture_control drone_bringup
source install/setup.bash
python3 -m colcon test --packages-select gesture_control drone_bringup
python3 -m colcon test-result --verbose
```

Resolve build/test failures before flight simulation. Package lint tests and
portable logic tests are distinct; lint is not flight validation.

For every subsequent ROS terminal first run:

```bash
cd ~/jedi_drone_ws
source /opt/ros/jazzy/setup.bash
source ai_env/bin/activate
source install/setup.bash
export ROS_DOMAIN_ID=77
export ROS_LOCALHOST_ONLY=1
```

Physically disconnect FC serial/USB and isolate other local ROS publishers.
Use only the following UDP SITL endpoint, never the serial launch default.
Start the previously built simulator (EEPROM wipe is intentional, simulation only):

```bash
screen -dmS ardupilot_sitl bash -c \
  'source ~/jedi_drone_ws/ardupilot_env/bin/activate && cd ~/jedi_drone_ws/ardupilot/ArduCopter && python3 ../Tools/autotest/sim_vehicle.py -v ArduCopter -N -w'
```

Terminal A, after the common ROS setup:

```bash
ros2 launch drone_bringup mavros_apm.launch.py fcu_url:=udp://:14550@
```

Terminal B, after setup:

```bash
ros2 topic echo /mavros/state --once
ros2 run drone_bringup flight_cmd_bridge
```

Check connected true, armed false, and simulator identity before starting the
bridge. If state differs, stop and investigate. Leave gesture and teleop stopped.
Terminal C, after setup:

```bash
python3 test_flight_cmd_bridge.py
```

Expect exit 0. This script takes off and lands the simulated drone; it checks
service acknowledgement and armed state, not measured altitude. Observe the
simulator and logs independently. For new commands, after a fresh simulated
takeoff, keep an acknowledgement observer running in another sourced terminal:

```bash
ros2 topic echo /flight_cmd_ack
```

In terminal C, send hold, check its OK acknowledgement and observed LOITER mode,
then emergency, check its OK acknowledgement and eventual disarmed state:

```bash
ros2 topic pub --once /flight_cmd std_msgs/msg/String "{data: open_palm}"
ros2 topic pub --once /flight_cmd std_msgs/msg/String "{data: hold}"
ros2 topic echo /mavros/state --once
ros2 topic pub --once /flight_cmd std_msgs/msg/String "{data: emergency}"
ros2 topic echo /mavros/state
```

Run these individually, waiting for each acknowledgement and simulator behavior
before the next command. Stop the state observer with Ctrl-C after disarming.
A FAIL, missing acknowledgement, wrong mode or failure to land is a failed check.
Do not infer success from `ros2 topic pub` delivery alone.

Camera-only validation: stop the bridge and all other command publishers, then
observe `/flight_cmd` in one terminal and start the camera node in another:

```bash
ros2 topic echo /flight_cmd
```

```bash
ros2 run gesture_control gesture_node --ros-args \
  -p debounce_frames:=5 -p hold_after_sec:=2.0 -p land_after_sec:=5.0
```

Check stable gesture debounce, two-fist emergency, missing-hand hold at 2 s and
land at 5 s total, and recovery. Never attach a physical FC for this check.
For keyboard publishing, stop the camera node and keep the bridge stopped:

```bash
ros2 run gesture_control keyboard_teleop
```

Verify t/open_palm, l/land, h/hold and space/emergency in the topic observer;
q exits. Terminal restoration and camera timing require this board check.
Stop foreground nodes with Ctrl-C and simulator with:

```bash
screen -S ardupilot_sitl -X quit
```

Record board versions, test output, simulator revision and failures in NIGHT_LOG.md.
Windows validation does not establish board/ROS/MAVROS/Quest compatibility.
