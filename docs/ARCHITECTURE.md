# Architecture and integration boundaries

```text
Camera index 0 -> gesture_node -> /flight_cmd -> flight_cmd_bridge
                       |                            | async workers
                safety.py                    MAVROS service adapters
                                                    |
                          /mavros/state <---- MAVROS <----> ArduPilot
                          /flight_cmd_ack <--- bridge

keyboard_teleop / dronectl -> /flight_cmd (one publisher at a time)
video_stream_server -> HTTP MJPEG -> viewer / Quest (independent camera access)
mock_server -> /telemetry -> dashboard / Quest HUD (no ROS telemetry adapter)
```

| Component | Inputs | Outputs / limits |
| --- | --- | --- |
| gesture_node | camera, MediaPipe landmarks | String /flight_cmd; change-only |
| safety.py | recognized hand labels + monotonic time | debounced gesture, hold, land, emergency |
| flight_cmd_bridge | /flight_cmd, /mavros/state | /flight_cmd_ack; MAVROS mode/arm/takeoff/land services |
| keyboard_teleop | foreground Linux terminal | /flight_cmd; no lease on exit |
| dronectl | explicit CLI arguments | dry-run default; explicit SITL-attested one-shot publish |
| MAVROS wrapper | configured FC endpoint | MAVLink; default serial endpoint is a placeholder |
| mock_server | fixed synthetic fixture | loopback HTTP JSON + static pages |

All newly added landing, rover, protocol, battery, geofence, arbiter, deadman,
vision and recording modules are standard-library Python. They have no ROS timers,
threads, hardware output or background network activity on import. They propose
values; integration requires independently reviewed adapters, frame transforms,
freshness, arbitration, safety guards and isolated SITL evidence.

The live bridge does not use the new arbiter. Multiple publishers remain unsafe.
Service success does not establish altitude or touchdown. FC state freshness and
companion-process failure are unresolved. JSON protocol CRC is not authentication.
No hidden routing, automatic disarm, FC failsafe changes or NPU integration added.
