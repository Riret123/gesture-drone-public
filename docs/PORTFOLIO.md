# Presenting the project honestly

Three-point pitch:

- Built a camera-to-ROS command pipeline with explicit debounce and missing-input
  behavior, while documenting service-result and companion-failure limitations.
- Separated portable control policies from hardware adapters and tested synthetic
  landmarks, state transitions, invalid inputs and protocol corruption on Windows.
- Explored a mobile landing pad through a disabled rover skeleton, parametric CAD
  concepts and reproducible simulation, with staged validation criteria.

## One-page summary draft

My project investigates how a natural user interface can request drone actions
through a modular robotics stack. A camera feeds OpenCV/MediaPipe hand landmarks;
ROS 2 carries gesture commands to a MAVROS bridge and ArduPilot. I separated policy
from transport so the control logic can be exercised without a camera or aircraft.

The most important engineering challenge is reasoning about failures. A command
acknowledgement reports service acceptance, not a completed maneuver. A companion
timeout cannot protect against companion power failure. The repository documents
these boundaries and requires isolated SITL before considering hardware tests.

I also explored a wheeled landing pad: pose-driven landing proposals, differential
drive, a versioned CRC protocol and repeatable toy landings. These additions remain
offline experiments. They demonstrate design and testing work, not validated
autonomous flight. The next milestones are calibrated frame transforms, stale-state
guards, SITL integration and independently supervised validation.

When using this draft, identify your own contributions accurately, acknowledge AI
assistance where applicable, and replace proposed work with evidence only after it
exists. Do not claim admissions outcomes, real landing accuracy or certified safety.

## 90-second demo script

0–15 s: show architecture and explain gesture-triggered commands.
15–35 s: run `python -B tests/run_all.py`; show a timeout and corruption test.
35–55 s: show the toy landing batch, labeling its model assumptions and limitations.
55–75 s: open the MOCK telemetry dashboard; explain that acks are not flight state.
75–90 s: show the phased roadmap and unresolved validation work. Use only simulator
footage unless separately authorized, documented hardware footage exists.
