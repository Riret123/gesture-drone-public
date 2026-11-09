# Recovery and staged acceptance

This is an evidence checklist for a beginner and an experienced test lead to use
together. Passing Python tests does not clear an aircraft for flight. No step here
authorizes this agent to arm motors. Record who ran each stage, date, firmware,
configuration, expected result, observed result and the decision to stop or advance.

## 1. Recover the source tree without hardware

1. Close duplicate editing sessions before repairing interrupted files. Preserve
   existing work; do not assume that the newest file is complete.
2. Read AGENTS.md, SAFETY.md, FINAL_REPORT.md, STATUS.md and LOG.md.
3. Inspect recently changed source, tests and configuration together. A syntactically
   valid duplicate function can hide an interrupted edit. A YAML key unsupported by
   the installed adapter is also an incomplete change.
4. Run `python -B tests/run_all.py` from the workspace. Require exit zero and the
   final unittest `OK`, not just a count of passing test lines.
5. Run `python -B tools/check_core_config.py config/core.yaml`. Resolve unknown or
   missing fields before startup. Record the test count and any unexecuted checks.

**Stop if:** files change under review, tests fail or hang, configuration fails,
or the source and installed package versions differ. Do not start a second writer.

## 2. Unpowered bench inspection

1. Remove every propeller and disconnect motor power. Keep the bridge and gesture
   command publisher stopped. Photograph labels locally without publishing identifiers.
2. With an experienced reviewer, match the physical PCB revision, manufacturer
   pinout, firmware target and documented wiring. Resolve ambiguity before wiring.
3. Check polarity, supply ratings, common ground, UART voltage compatibility and
   strain relief against the actual component documentation. Do not guess pins.
4. Use camera-only preview with the bridge stopped; close preview before another
   camera program starts. Confirm missing hand and both hand orientations visibly.
5. On the target, use the read-only doctor without camera capture first. An optional
   camera probe requires exclusive camera ownership. Topic presence is not proof
   of a healthy publisher, authentic hardware or safe flight state.

**Stop if:** wiring/identity is uncertain, there is heat or smell, a camera owner
conflicts, telemetry disagrees with physical state, or the doctor reports failure.

## 3. Isolated simulator acceptance

1. Disconnect physical FCs and isolate other ROS participants. Follow SITL.md for
   the simulator endpoint, one command publisher and plan-only scenario review.
2. Run normal, hold, land, emergency and approved simulated fault scenarios using
   the installed ROS/MAVROS interfaces. Keep raw evidence outside source control.
3. Observe actual mode, armed state, altitude and landing; service acceptance is
   insufficient. Verify fault restoration even after a failed scenario.
4. Verify landing inhibits later open palms and hold, then verify the documented
   explicit reset contract. Confirm process restart behavior separately.

**Stop if:** a physical endpoint could be reachable, a request has an uncertain
outcome, altitude is unobserved, reset unexpectedly permits takeoff, fault recovery
fails, or an independent pilot recovery path is unavailable.

## 4. Props-off motor verification, human operated only

1. Obtain a separate powered-test decision from the responsible experienced
   operator after completing the unpowered and simulator gates. Props off alone
   is not permission to arm. Keep all agent control nodes stopped.
2. Have that operator review the installed firmware's official motor-test procedure,
   frame diagram, ESC protocol, restraint, exclusion area and immediate isolation.
3. Prepare an output-to-motor sheet: test label, physical location, expected
   direction and observed direction. The operator selects the procedure's limits;
   this guide supplies no motor command, throttle, duration or arming sequence.
4. Disconnect motor power after the campaign and independently review the sheet.

**Stop if:** anyone enters the exclusion area, restraint moves, motor identity or
direction differs, isolation is unreliable, or there is abnormal sound or heating.

## 5. Tether review

1. Begin unpowered. Ask a qualified engineer to review fixture loads, anchor
   ratings, clearances, entanglement, controller response and remote isolation.
2. Record numeric abort limits specific to the approved fixture. Do not improvise
   rope dimensions, load ratings or indoor flight from this guide.
3. Any powered trial is a separate human-led campaign with pilot and spotter.

**Stop if:** the fixture has no reviewed load case, any line can reach a propeller,
an anchor can move, or a pilot cannot safely abort. A tether is not flight clearance.

## 6. First hover, qualified pilot only

1. Require reviewed calibration, motor mapping, pack-specific battery monitoring,
   receiver failsafe, estimator health and independent pilot authority.
2. The test lead approves the legal site, weather, exclusion area, observers,
   flight envelope, battery reserve and abort plan before fitting props at the site.
3. Complete pilot-controlled hover and landing before considering gesture control.
   Gesture flight requires a later separate review of camera evidence and latency.
4. Review logs and physical condition before another trial; an ACK is not a landing.

**Stop if:** attitude, vibration, drift, voltage sag, latency, link health or observer
contact exceeds the recorded limits. The qualified pilot follows the approved
recovery procedure; do not invent a universal disarm-in-air response.
