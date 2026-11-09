# Bill of materials — concept, not a purchasing recommendation

Prices and part ratings must be verified from chosen vendors; no live pricing used.

| Item | Quantity | Selection / validation | Unit price |
| --- | ---: | --- | --- |
| Orange Pi 5 Pro | 1 | existing target in code; power and thermal budget unverified | TBD |
| AERO SELFIE H743 | 1 | source-identified FC; pinout/firmware/wiring unverified | TBD |
| Camera | 1 | Linux index-0 access, downward calibration for landing | TBD |
| ESP32 or Pi Pico | 1 | watchdog-capable MCU; choose logic voltage | TBD |
| Geared motor + encoder | 2 | mass, torque, speed, stall current measurements | TBD |
| Dual H-bridge | 1 | above stall current, thermal and logic compatibility | TBD |
| Rover battery + charger | 1 each | chemistry/voltage/fuse reviewed together | TBD |
| Regulator / fuse / disconnect | 1 each | peak loads, estop architecture | TBD |
| Wheels / caster | 2 / 1 | traction, guarded pinch points, stability | TBD |
| Pad surface + fiducial | 1 | known marker size, non-slip surface | TBD |
| Contact sensor | TBD | independent touchdown evidence | TBD |
| Printed brackets / frame | 1 set | non-flight-qualified CAD concepts below | TBD |

`cad/camera_mount.scad`, `cad/pan_tilt_bracket.scad`, `cad/landing_pad_frame.scad`
are simple parametric millimeter concepts. Review dimensions, fastener clearances,
servo/camera fit, material, print orientation, mass and structural loads before use.
No STL outputs committed. OpenSCAD rendering and physical fit have not been tested.
These models are not certified load-bearing or flight-ready parts.
