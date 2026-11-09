# Core status

Latest portable suite: **857 tests passed**, exit 0. The last manifest-wrapped
run passed 829 tests via `python -B tools/verify_portable.py`, covering 228
source/test/tool/script/config files with no endpoint drift. This is not an
immutable snapshot or evidence of target execution.

A two-hour offline seeded stress campaign is RUNNING (seed 20261109).
Latest recorded checkpoint: 3,821.4 seconds, 1,093,873 cases, 109,387,300 command steps,
4,375,492 geometry checks, 21,878 real-thread boundary trials; no assertion or
tracked-core source drift. Final result is not yet available.
One ~581-second reporting gap occurred; cause unverified. This is elapsed-time
campaign evidence, not uninterrupted CPU load or target real-time measurement.

Implemented and tested on Windows:

- Bounded service waits/responses, independent cumulative three-failure circuits,
  single in-flight callback per operation/mode, zero automatic actuation retries.
- Reception-time landing latch; hold inhibition; every live bridge startup begins
  inhibited. Explicit operator_reset requires five seconds of advancing connected/
  disarmed receive samples, each <2 s old, gaps <2 s, and idle workers.
- Epoch cancellation before/after state reads and service waits; already-submitted
  calls remain uncancellable. No external/native submission atomicity is claimed.
- FC-loss best-effort emergency; completed-frame heartbeat supervision for gesture
  process/native stalls after first health. Same-host v1 session/sequence/0.5 s
  age gate, depth-one history; explicit reset re-enables supervision.
- 70 generated controller command cells and 240 actual primitive-adapter cells;
  race/property tests, CSV replay, fake FC and injected RC/battery/link-loss events.
- Optional identity-bound saved 3D world profile, confidence abstention and
  negotiated-camera checks; default empty path keeps 2D. Default returned-frame
  budget 200 ms; camera requests 640x480/30 fps/model 0.
- Core YAML schema/CLI, offline calibration/benchmark/stress tools, read-only doctor
  with bounded combined output, single-state parsing and topic/service type checks.
- Board/SITL script line review and startup fixes; beginner/performance guides.

Further audit: explicit FCU launch endpoint (no default physical serial route),
legacy SITL fail-fast/cleanup/latch checks, strict/frozen calibration capture
refusal, oversized CSV diagnostics, actual CSV-to-adapter startup/reset chain,
doctor scalar/type validation and MAVROS backend contract review. The backend
can serialize landing behind an ACK wait; local worker reservation is not FC
priority. See MAVROS_CONTRACTS.md.

Camera-only world recorder added, plan-only without --capture, with external
new-file-only output and no images/ROS/FC activity. Inert capture/cleanup tests pass;
actual board capture remains unexecuted. Canonical ACK and pending-future cleanup
helpers are prepared/tested but deliberately not yet integrated into the frozen
live core; R29/R30/R31/R35/R36 integration follows the timed campaign.

Concurrent recovery work was preserved: strict doctor ambiguity checks, AST
structure regressions, replay mutation campaign, RECOVERY_ACCEPTANCE.md,
ORANGE_PI_MEASUREMENT.md and its 28-item backlog. The primary continuation added
26 further red-team tasks and continued several. Earlier 446/552/558/etc. counts
are historical; they are not competing current suite results. Ownership
clarification was requested after detecting external edits; no answer recorded.

Unverified: Linux/ARM dependency reproducibility, colcon/ament, Bash/systemd,
installed MAVROS/executor contracts, real camera/MediaPipe orientation accuracy,
thermal/exposure/latency performance, actual SITL physics/failsafes, PCB/UART/motor
mapping, powered bench/tether/hover. Commands/reset/heartbeat are unauthenticated;
command/ACK request IDs and source arbitration remain pending. RC/battery harness
events are not live safeguards. FC failsafes and an independent pilot are required.

No git commands, prohibited directory access, secrets, physical motor arming or
live flight commands were performed. Five empty failed-test directories remain
after automatic cleanup rejection; details are in LOG.md. See FINAL_REPORT.md
for the current human handoff and BACKLOG.md for acceptance tasks.
