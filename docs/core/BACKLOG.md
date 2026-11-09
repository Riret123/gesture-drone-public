# Core P0/P1 backlog

## Continuation red-team campaign (new acceptance tasks)

The original list still contains target-only work. These additional tasks arise
from reviewing the new implementation; checked items mean portable logic only.

- [x] RT01: Prohibit overlapping callbacks within one service/mode circuit; reserve independent land operation.
- [x] RT02: Release circuit in-flight reservation on KeyboardInterrupt; test later land admission.
- [x] RT03: Preserve an existing file on atomic-profile temporary-name collision.
- [x] RT04: Re-enable gesture/FC-loss watchdogs after explicit reset without renewing old health.
- [x] RT05: Version heartbeat envelope and reject repeated sequence/session replays (unauthenticated).
- [x] RT06: Depth-one heartbeat history and 0.5 s same-host source-age rejection; real ROS timing pending.
- [x] RT07: Prevent restart bypass by requiring startup latch/dwell/reset on every live bridge launch; no disk persistence needed.
- [ ] RT08: Bind reset confirmation to an authenticated operator/source identity.
- [ ] RT09: Add command session IDs and ACK correlation before same-command retry campaigns.
- [ ] RT10: Confirm local future cleanup after response timeout on installed rclpy.
- [ ] RT11: Measure whether service discovery respects its timeout under executor starvation.
- [ ] RT12: Verify landing capacity during simultaneous camera-stall and FC-loss callbacks.
- [ ] RT13: Exercise successful reset versus queued older landing in a real multithreaded ROS executor.
- [ ] RT14: Validate watchdog behavior if FC disconnects before the first received connected state.
- [x] RT15: Cached/pre-latch snapshots cannot accumulate reset dwell even with max_age=10; target telemetry timing still unmeasured.
- [x] RT16: Preserve literal quoted comment markers while rejecting unsupported YAML consistently.
- [x] RT17: Check negotiated width/height/fps against deployment profile; target measurements pending.
- [ ] RT18: Measure MediaPipe package/model identity stability across Linux ARM updates.
- [x] RT19: Profile read failure rejects before camera acquisition; strict malformed-profile unit tests.
- [ ] RT20: Collect held-out back-of-hand fists with occlusion, distance and motion labels.
- [ ] RT21: Capture actual exposure/dequeue timestamps and buffering uncertainty, not only callback time.
- [ ] RT22: Measure watchdog emergency delay under thermal throttling and CPU contention.
- [ ] RT23: Audit doctor behavior when topics exist but required publishers are absent or stale.
- [ ] RT24: Validate user-service stop timeout and hung-native-child cleanup on Linux.
- [ ] RT25: Compare motor-test letters against verified frame output map with powered-test lead.
- [ ] RT26: Independently inspect tether load/entanglement/abort design before powered testing.

Checkboxes mean implemented logic, not measured deployment acceptance. No P2/P3
work is scheduled until P0/P1 acceptance is complete.

- [x] Live malformed/collapsed landmark rejection and FC receive-age watchdog.
- [x] Cancellation during service waits and before delayed worker execution.
- [x] Bound workers with reserved landing capacity; reject busy commands unqueued.
- [x] Observe GUIDED/armed transitions before advancing takeoff.
- [x] Mocked full chain and actual adapters with request/timeout/failure tests.
- [x] Manual board services/log capture, never enabled or executed.
- [x] Sourced bring-up checklist with unresolved board identity gate.
- [x] Five scenario plans and mock transport contracts, not live SITL.
- [x] Guarded ROS SITL adapter and fresh flight-outcome observation contracts,
  tested with mocks only; actual simulator execution remains pending.
- [x] Read-only bounded APJ board-ID/size/hash checker; physical identity unresolved.

## P0 pending

- [ ] Confirm PCB revision, manufacturer pinout and exact firmware target.
- [ ] Record firmware image/version/hash and backup/restore procedure.
- [ ] Confirm Orange Pi OS/workspace/UART pinmux/device/logic levels/baud.
- [ ] Reproduce Linux/ARM dependencies with required MediaPipe API.
- [ ] Run colcon build/tests and verify installed interpreters.
- [ ] Review and execute ROS SITL adapter on the installed MAVROS interfaces.
- [ ] Establish altitude/position tolerance and dwell from simulator traces.
- [ ] Add firmware-specific RC fault injection and restoration in isolated SITL.
- [ ] Execute takeoff/hold/land/emergency/RC-loss scenarios and retain evidence.
- [ ] Test monitored GCS heartbeat loss separately from gesture-node loss.
- [ ] Configure measured battery and receiver-specific FC failsafes.
- [ ] Design landing-completion/rearm latch; busy guard ends at service return.
- [ ] Validate physical motor map/direction in a separate approved props-off test.
- [ ] Complete accelerometer/compass/radio/battery/ESC-specific calibration.
- [ ] Validate Bash/systemd/device permissions on target Linux.
- [ ] Test shutdown/service concurrency against a real ROS executor.
- [ ] Add request IDs to a reviewed versioned command/ACK protocol.
- [ ] Add observed, bounded live-test recovery without blind takeoff retries.
- [ ] Review independent pilot authority and each FC fallback condition.
- [ ] Complete qualified pilot-only hover before gesture-controlled flight.
- [ ] Engineer a rated tether fixture with entanglement/load/abort review.

## P1 pending

- [ ] Collect consented front/back/side-on datasets with independent labels.
- [ ] Evaluate joint angles on held-out sessions and users.
- [ ] Validate world-landmark scale, handedness and occlusion behavior.
- [ ] Measure false takeoff/emergency, missed fist and abstention metrics.
- [ ] Persist calibration with strict version/model/camera identity schema.
- [ ] Select confidence gates from held-out evidence before live integration.
- [ ] Add supervision that survives native camera/inference stalls.
- [ ] Measure exposure age, buffering and camera reconnect on Orange Pi.
- [ ] Collect thermal/CPU-contention latency traces against provisional budgets.
- [ ] Add process heartbeat supervision without unsafe restart/rearm.
- [ ] Reject stale ROS commands with versioned session/time metadata.
- [ ] Review command-source arbitration and ROS graph authentication/isolation.
- [ ] Test boot, camera restart and simulator reset reacquisition semantics.
- [ ] Package/version core YAML and reproduce deployment from transferred sources.
- [ ] Complete fresh audit of remaining existing modules after core priorities.

The requested list is not exhausted. These are substantive unfinished tasks, not
claims that hardware is finished or that every existing module has been audited.


## Recovery red-team follow-up (2026-11-09)

These are new acceptance tasks; check only with recorded evidence, not a mock claim.

- [x] R01 Reject duplicate/contradictory doctor connected/armed fields with regressions.
- [x] R02 Detect shadowed Python definitions and adapter methods nested in main.
- [x] R03 Bound combined doctor stdout/stderr during capture; overflow/timeout terminate direct child and fail closed. Linux descendant cleanup still pending R23.
- [x] R04 Require a bounded single ROS state subset document in doctor; reject nested/split safety fields and extra documents.
- [ ] R05 Verify doctor state freshness with source timestamp and clock uncertainty.
- [x] R06 Doctor checks all three topic and four FC service types; wrong-type regressions pass with inert probes.
- [ ] R07 Verify calibration identity includes camera rotation/crop/flip configuration.
- [ ] R08 Test world-landmark left/right association under reordered model outputs.
- [ ] R09 Measure fist occlusion failures for back-of-hand and side-on views.
- [ ] R10 Test profile file replacement during loading and failed identity updates.
- [ ] R11 Measure delivered camera settings versus requested settings at startup.
- [x] R12 Inert actual-adapter test: continuous over-budget two-fist frames still hold/land by input-loss deadlines. No camera timing or immediate-emergency guarantee for stale frames.
- [ ] R13 Test heartbeat before any command, before first frame and after ROS reconnect.
- [ ] R14 Reject replayed/forged heartbeat in a reviewed authenticated protocol.
- [ ] R15 Exercise reset-to-next-watchdog-tick takeoff races with real executor schedules.
- [ ] R16 Define persistent landing inhibition across bridge crash/reboot without auto-rearm.
- [ ] R17 Test repeated FC loss/reconnect after reset with stale queued telemetry.
- [ ] R18 Separate pre-submit cancellation from uncertain post-submit failure accounting.
- [ ] R19 Review circuit recovery without restarting away the landing latch.
- [ ] R20 Test simultaneous land and emergency against installed MAVROS service behavior.
- [ ] R21 Measure time to FC action when bridge dispatch is CPU-starved.
- [ ] R22 Record per-stage latency across sustained thermal throttling and recovery.
- [ ] R23 Validate Linux service stop kills descendants without issuing new commands.
- [ ] R24 Verify configuration parser behavior for quoted hash characters and escapes.
- [ ] R25 Run malformed landmark CSV mutation corpus with bounded memory/time evidence.
- [ ] R26 Independently review beginner acceptance gates with an experienced pilot.
- [ ] R27 Establish immutable test/source manifest before target acceptance campaigns.
- [ ] R28 Reconcile installed package configuration and interpreter with reviewed sources.

Further source-review findings to implement/measure:

- [ ] R29 Distinguish policy/pre-submit cancellation from backend failures in circuit accounting.
- [ ] R30 Keep bridge executor alive and acknowledge thread-start failure instead of propagating it.
- [ ] R31 Bound/remove locally pending ROS futures after timeout without claiming FC cancellation.
- [ ] R32 Measure backend command-group landing delay while arm/takeoff ACK waits are stalled.
- [ ] R33 Confirm /mavros/state publishes advancing observations at adequate frequency for reset dwell.
- [ ] R34 Reject unusable FPS/debounce/input-loss combinations with reviewed cross-parameter rules.
- [ ] R35 Integrate canonical ACK framing so unknown text cannot reflect an accepted-command prefix (pure helper/tests implemented).
- [ ] R36 Block takeoff if landing circuit is open or the landing service is unavailable; test reset/circuit interaction.
- [ ] R38 Use one final immutable state snapshot plus epoch guard, avoiding another state read after the mode/armed submission check.
- [ ] R39 Include admitted-but-not-started workers in the public operator-reset idle gate (admission helper implemented).

R01/R02 were continued immediately after adding this follow-up: portable regressions
pass. Remaining tasks need additional implementation or target evidence. See
RECOVERY_ACCEPTANCE.md and ORANGE_PI_MEASUREMENT.md for staged human gates.
