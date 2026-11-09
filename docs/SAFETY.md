# Safety and changed behavior

MAVROS launch now requires an explicit fcu_url argument; the former physical
/dev/ttyUSB0:921600 placeholder is no longer selected by omission. GCS forwarding
remains empty by default and target IDs remain 1/1. This changes endpoint-selection
behavior; real installed launch/MAVROS acceptance is still pending.

Continuation overrides older rearm statements below: fist/land/emergency latch
takeoff inhibition at reception, including failed/busy landing requests. Hold
cannot replace this latched landing. The explicit operator_reset command clears
the latch only after five seconds of observed connected/disarmed state and idle
workers; observation gaps >=2 seconds restart dwell. Commands remain unauthenticated:
isolate publishers. Every live bridge startup now starts inhibited and requires
the same dwell/reset, preventing restart bypass without disk persistence.
Operator authentication remains unresolved. A 0.2-second watchdog attempts emergency
once per session when a previously connected FC becomes unavailable. A dead link
cannot deliver that request. Each operation/mode circuit stops submissions after
three cumulative failures until process recovery; no automatic request retries,
including uncertain arm/takeoff. Landing has an independent circuit. These new
guards have only portable mock validation; FC failsafes remain essential.

New camera requests default to 640x480 at 30 fps, model 0. Optional
pose_profile_path (empty by default) loads version/camera/model-bound 3D world
calibration; missing/mismatched world outputs abstain, with confidence margin >=.5
and no 2D fallback. Actual negotiated geometry/FPS must match an enabled profile.
Returned frame processing over 200 ms default becomes missing input. These are
changed live gesture gates, not measured camera accuracy or exposure freshness.

A completed-frame heartbeat lets the separate bridge detect gesture process or
native-call stalls after the first accepted heartbeat; 3 s default triggers one
emergency request per session. Heartbeat v1 requires session/advancing sequence,
depth-one history and source age <=0.5 s on the SAME HOST monotonic clock domain.
Reject future/old/duplicate/changed-session messages. Explicit operator reset
re-enables supervision without refreshing stale input; a source session change
requires that reset. This is unauthenticated and cannot protect against bridge
death, companion power loss or a failed FC transport. No automatic restart or
automatic disarm is introduced. Validate all changed timings in isolated SITL.

Current core changes and residual hazards are in core/LOG.md, core/AUDIT.md and
core/BACKLOG.md. The live script now requires --sitl-isolated, fresh connected/
disarmed initial state and command-matching ACKs. This attestation does not detect
hardware; historical statements below about no guard describe the older script.
The bridge waits up to 5 seconds (state_transition_timeout_sec) for observed
GUIDED/armed transitions, then rechecks mode/armed state before submission.
Bounded worker admission reserves landing capacity; busy commands FAIL unqueued.
Safety input invalidates pending takeoff immediately; already sent calls remain
uncancellable. Landing remains inhibited until the explicit observed reset.
Returned camera/inference exceptions advance input-loss timers; the separate
bridge supervises completed-frame heartbeat stalls as described above.
These guards are not hardware validated.
Existing ratio 1.1, altitude 2 m, debounce 5 and input-loss 2/5 s defaults remain.


Never arm real motors during these tests. Remove propellers and disconnect motor
power before hardware bench inspection. Props off does not authorize arming.
Physically isolate flight controllers and other ROS participants and verify MAVROS
uses the SITL UDP endpoint before any integration script. Attestation flags do
not detect hardware.

New defaults: 5 consecutive identical valid frames; missing/unrecognized input
requests hold after 2 seconds, land after 5 seconds total since the last confirmed
valid gesture (not 5 additional seconds). Mixed gestures are invalid. Two fists
request emergency immediately, bypassing debounce. The classifier's 1.1 ratio
threshold and takeoff altitude of 2.0 m are unchanged. ROS startup parameters:
`debounce_frames`, `hold_after_sec`, `land_after_sec`; require positive frames and
0 < hold < land. Only confirmed valid gestures renew the timeout.

`open_palm`: GUIDED -> arm unless already armed -> takeoff 2.0 m.
`fist`, `land`, `emergency`: land service, skipping only known disarmed state.
`hold`: LOITER, skipping known disarmed state. No fallback to GUIDED: selecting
GUIDED alone does not establish a position hold target. Check LOITER prerequisites
in SITL; a rejected mode request is acknowledged FAIL, with no hidden fallback.
Unknown/disconnected FC state rejects takeoff. No automatic disarm is introduced.

Safety commands invalidate later steps in a running takeoff sequence. Duplicate
in-progress takeoffs/landings are skipped. Service requests already sent cannot
be cancelled, and concurrent FC service ordering cannot be guaranteed. Timeouts
remain 5 seconds for service availability and 5 seconds for a response; a timeout
does not prove the FC did not execute the request. Acknowledgements describe service
acceptance, not completed flight or verified altitude. FC state expires after
2 seconds on the local receive clock (state_max_age_sec). Stale state blocks
takeoff and cannot suppress landing/hold. This is not a process-death watchdog.
Command sources are not arbitrated or authenticated: use one publisher
at a time. Open palm after landing fails until the explicit reset contract passes.

Gesture outputs publish only on changes. The companion failsafe cannot protect
against bridge death or failed companion power. The heartbeat guard only helps
when the separate bridge and FC path remain alive. It is not a replacement for
FC-level failsafes and an independent pilot.
A continuous valid open palm renews the lease; it is not a deadman switch.
Keyboard teleop has no lease/watchdog: quitting or terminal loss sends no command.
The Quest viewer sends no commands; deadman design notes are in QUEST_HUD.md.

Validate each behavior in SITL before considering any controlled hardware work.
No hardware flight authorization or safety certification is provided by unit tests.

## New offline experiments

Landing/rover control, geofence, battery policy, arbitration, Quest deadman, velocity,
PID, filtering, contact confirmation, frame conversion, freshness and slew limits
are offline experiments. They are NOT wired into the live ROS bridge or gesture
node and do not add safeguards to a running vehicle. See OFFLINE_POLICIES.md and
the per-task NIGHT_LOG.md entries for proposed parameters and validation limits.
No FC parameters, MAVLink routing, live altitude, arming order or gesture thresholds
were changed in this autonomous backlog run. The additional classifier is opt-in.

The new dronectl entry point defaults to dry run; explicit --send and
--sitl-isolated attestations are required to publish once. These flags do not
detect hardware or verify flight acknowledgements. Never use them against a
physical aircraft. Multiple live publishers remain unarbitrated.

The rover firmware has no configured pins or enabled motor driver. Browser HUDs
remain view-only. The development telemetry server binds loopback and returns
mock data. Toy simulation success is not hardware landing evidence.

## Company-run offline validation strengthening

New company experiments remain disconnected from ROS control. Missions, fleet
separation, tag quality/capture/motion gates, sensor provenance, energy arithmetic
and read-only telemetry/replay analyses do not authorize flight or provide live
FC safeguards. Explicit experiment limits and model omissions accompany their
role records under docs/company/. No live modes, altitude, arming order, gesture
thresholds, FC parameters or MAVLink routing are changed by these additions.

The existing offline Deadman helper now rejects non-advancing sample timestamps
and revokes its remembered release after an invalid/reversed local clock. This
requires distinct timestamps for a release and later press; it is a stronger
input contract, not a headset transport or operational deadman. Its default
timeout remains 0.25 seconds. Velocity/slew helpers reject malformed/bool numeric
configuration consistently; stable normalization avoids overflow-induced zero
direction, and unrepresentable steps reject. Defaults remain unchanged. None of
these helpers is wired to the live bridge. See frontend/ROUND04_CONTROL_AUDIT.md
under docs/company/ for regressions and behavior limits.

The shared mock dashboard/Quest display has stricter schema, response-size,
display-expiry and visibility handling. Those are view-only presentation checks,
not flight-safety timeouts. Browser/Quest rendering and real telemetry acquisition
are still unverified. Replay analytics emits aggregates only and never commands.
