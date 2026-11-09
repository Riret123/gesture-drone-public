# Mobile landing pad concept

An experimental differential-drive rover carries a flat fiducial landing pad.
The drone observes a known-size AprilTag/ArUco marker; a future calibrated adapter
must convert its pose into the camera convention below. No detector or flight
transport is supplied by this concept. First land on a stationary pad in simulation.

```text
          drone / downward camera
                   |
           +---------------+
           |   TAG  PAD    |  non-slip, unobstructed surface
           +---------------+
            O [battery] O     guarded wheels / low center of mass
              [MCU/driver]
```

Electronics: ESP32 or Pi Pico, two geared DC motors with encoders, a dual H-bridge
rated above measured stall current, fused battery, regulator, physical motor-power
disconnect, emergency stop and optional wheel odometry. Select voltages and ratings
from actual parts; no wiring pinout or verified motor driver is implied.

Safety: props removed and motor power disconnected for bench inspection; never arm
real motors. A landing pad is not a person carrier. Keep people clear of the pad
and wheel pinch points. CRC is corruption detection, not authentication. Rover
motion stops on link timeout. FC failsafes and independent pilot remain necessary.

Phases: dimensional CAD review; unpowered fit; software-only simulation; rover
bench tests with drive power disconnected; controlled rover-only testing; isolated
SITL integration; independently reviewed tethered tests; authorized flight trials.
Require measured marker error, contact sensing, relative speed and stopping distance
before any moving-pad trial. See SAFETY.md and ROADMAP.md.
