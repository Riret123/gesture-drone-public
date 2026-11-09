# Core flight run log

## Continuation: service circuit and landing latch (2026-11-09)

Batch 49 full-suite result: 808 passed, exit 0.

Batch 50: reset freshness red-team found cached FC state could manufacture dwell
when max_age was configured above five seconds. Immutable snapshots now carry
receive time; reset requires distinct advancing receive samples spanning five
seconds, each <2 s old, gaps <2 s and no pre-latch sample. Added three regressions;
full suite 811 passed. This tightens reset behavior, not FC state-age defaults.

Batch 51 in progress: repeated permission check after final state read, plus
controller/permission epoch recheck if safety arrives inside state getter. Tests
inject landing exactly at these reads. There remains an uncancellable external
submission boundary; no lock is held across potentially blocking FC/native calls.

Batch 48: preserved concurrent recovery edits (strict doctor state parsing,
source-structure and replay mutation tests, recovery acceptance docs/backlog).
Requested ownership clarification after discovering the other writer's checkpoint;
no reply at this checkpoint. Counts include those external additions. No git or
immutable checkout snapshot was used. Updated safety/gesture/SITL docs to reflect
live startup inhibition, calibration activation, frame budget and same-host
heartbeat freshness rather than stale historical no-latch claims.

Batch 49: continued recovery task R03 with a separate bounded_probe helper and
small doctor integration, preserving the external strict state parser. Combined
stdout/stderr has a 16 KiB capture cap before further allocation, eight-second
default run limit, direct-child termination, invalid-UTF8 refusal and no shell.
Harmless local Python-child tests cover huge stdout/stderr, timeout, exit status
and argument bounds. No ROS/camera/FC probes executed. Descendant/process-group
cleanup still requires Linux acceptance; direct-child kill is not that guarantee.

Batch 46: 240 generated actual-adapter primitive cells (five operations x six
modes x connectivity x armed state x latch) added to 60 controller command cells.
Full suite 802 passed. These finite abstractions do not prove arbitrary FC or
middleware state spaces.

Batch 47: restart red-team identified latch loss on process restart. Actual live
bridge now constructs startup_latched=True on every launch; observed five-second
connected/disarmed dwell plus explicit operator_reset is required even for first
SITL takeoff. Offline controller/harness defaults remain opt-in for startup latch.
Actual constructor test initially failed because its fake clock reversed after a
real-clock reset attempt; moved clock installation before observations. Full
suite 803 passed. SITL/service/table docs updated; no actual ROS launches.

Batch 43: 26 concrete new red-team backlog items added; continued implementing
them. Single in-flight callback per circuit; interruption cleanup; exclusive
profile collision preservation; minimum deployment confidence/gap; quoted YAML
comment handling; heartbeat v1 session/sequence/source-age validation and depth-one
queues. Heartbeat age requires both nodes on the same OS monotonic clock domain.
Full suites progressed through 549, 554 and 558 passing tests.

Batch 44: pure-Python classification benchmark measured 400 Windows AMD64 samples
(p50 0.0701 ms, p95 0.0807 ms, max 1.7879 ms); excludes MediaPipe/camera/ROS/FC.
Recorded timestamp arithmetic fixture and docs added, no board-speed claim.
Full suite 559 passed. Wrote FIRST_TESTS.md and PERFORMANCE.md, with official
ArduPilot and MediaPipe source references. Physical powered steps require the
hardware-specific human gate; no generic motor throttle or tether loads invented.

Batch 45: saved profile startup validates negotiated camera width/height and FPS
within 10 percent; mismatch releases camera without starting inference. Camera
identity includes requested resolution/FPS/mirror policy. Invalid/missing profile
rejects before camera acquisition. Full suite 562 passed. No real camera tested.

Batch 42: opt-in pose_profile_path activates version/camera/model-matched 3D
world-landmark classification; absent/mismatched world outputs abstain without
2D fallback. Default empty path keeps 2D. New default 200 ms returned-frame
processing budget rejects slow frames as missing input. Completed-frame heartbeat
allows the separate bridge timer to request emergency after 3 s without a
heartbeat, once per session after first heartbeat. Handles gesture process/native
stall, not bridge/companion death. Added exact-boundary/slow-frame/world-output
tests. Full suite 544 passed. A provisional inherited-test fixture accidentally
ran existing cases twice (568); removed duplicate discovery, no coverage lost.
Reset re-enables watchdogs without refreshing stale heartbeat; regression added.
Offline world-CSV calibration CLI added; no real recordings were collected.

Batch 40 completed: shell/template/ROS runner reading and startup fixes described
below. Full suite 531 passed. No shellcheck/Bash/systemd runtime claim.

Batch 41: shared frame classifier used by actual gesture_node and pure replay.
Bounded strict landmark CSV fixtures, deterministic fake camera/FC/MAVROS service
recording, normal flight, input loss, flicker, two fists, duplicate commands and
explicit RC/battery/link-loss supervisory events. Landing acceptance intentionally
leaves fake FC armed. RC/battery events are injected only: no new live telemetry
subscriptions or automatic battery thresholds. Full suite 540 passed. The existing
actual-adapter chain test still passes. This is deterministic command simulation,
not flight physics or a real ROS executor.

Batch 39: aligned individual ROS startup override bounds with file-schema bounds;
full suite 527 passed. Added read-only board doctor for ROS environment, required
topics/services, returned connected/disarmed state, serial/camera presence, disk
space and time synchronization. Optional camera capture runs in a separate
eight-second-bounded child. No image, credentials or raw environment are printed.
Mock-only doctor tests and full suite: 531 passed. Camera probe is not live
gesture-process supervision and does not measure exposure age.

Batch 40 in progress: read every line of board core.sh, service/environment
templates, SITL scenario.sh and Python ROS scenario runner. Found unnecessary FCU
URL requirement for camera-only startup and late unknown-component rejection;
fixed both. Added descriptive missing environment-file checks and YAML validation
before control startup. Bash/systemd remain unexecuted on Windows.

Batch 36: strict versioned calibration JSON persistence with bounded reads,
camera/model identity, duplicate/nonfinite rejection and atomic replacement.
Write-failure preservation tests pass. It is not enabled in live classification.
Full suite: 522 passed. Windows TemporaryDirectory mode permissions caused a
hang inside NamedTemporaryFile retries; interrupted the two test processes and
replaced that path with ordinary workspace test directories and exclusive file
creation. Automatic approval review rejected removal of five empty failed-test
directories (tmp4i8g6gq4, tmp7mchoq_a, tmpm8pzw6qn, tmpy8718hcq, tmpyflz_vp1).
They remain for human cleanup; the older tmp2p5s1_t6 was not touched.

Batch 37: bounded camera width/height/fps/model options (defaults now explicitly
request 640x480 at 30 fps, model 0); full suite 524 passed. Drivers may reject or
negotiate settings; actual capture rate/latency remains unmeasured.

Batch 38: numeric core YAML subset parser and complete schema with duplicate,
unknown-key, nonfinite/type/bounds checks and hold-before-land ordering. Read-only
tools/check_core_config.py requires no third-party YAML library. Full suite 527
passed. Unsupported general YAML constructs deliberately reject. Startup override
bounds are being aligned with this reviewed schema.

Read AGENTS.md, SAFETY.md, FINAL_REPORT.md, STATUS.md and this log first.
No git commands or network/ access, live ROS, camera, FC,
motor, service installation or external communications were used.

Batch 34: added operation-isolated cumulative three-failure service circuits,
zero automatic actuation retries, reception-time landing latch, and explicit
operator_reset after five seconds connected/disarmed observations. Observation
gaps >=2 seconds, reversed/invalid clocks and armed/disconnected samples reset
the dwell. Hold cannot override latched landing. One old test failed because it
expected rearm after a landing exception; it now verifies persistent inhibition.
Generated 60 abstract state/command cases, reset/race tests and a deterministic
10,000-step property campaign. Full suite: 513 passed.

Batch 35: actual bridge reception, busy admission, thread-start failure and circuit
adapter tests; 0.2-second timer attempts emergency once per process after a
previously connected FC becomes unavailable. It also samples reset eligibility.
No claim that a broken link can deliver landing; independent FC failsafes remain
required. Full suite: 518 passed, direct process exit 0. An earlier PowerShell
stderr pipeline reported shell exit 1 while unittest said OK; direct invocation
was used to confirm success. New circuit and latch are live behavior changes,
not SITL or hardware validated. Already-sent requests remain uncancellable.

## 2026-11-09: baseline and first safety batches

Read AGENTS.md, docs/SAFETY.md, BACKLOG.md, NIGHT_LOG.md and company records.
Company records describe historical offline work; their unfinished timing and
role plans are not evidence of current flight readiness. Current priority is P0/P1.
Baseline: 343 portable unittest cases passed on Windows Python 3.12.

Batch 1: wrote five regressions first. Observed six failing assertions and two
errors for malformed classifier inputs, collapsed geometry, mid-sequence
disconnect and disconnected-disarmed emergency skip. Fixed live classifier to
return other for malformed/nonfinite/bool/extreme/collapsed geometry; unchanged
1.1 curl ratio. FC connectivity rechecked before each takeoff step. Landing/hold
skip now requires connected, explicitly disarmed state. Full suite: 348 passed.

Batch 2: wrote watchdog tests before implementation; suite failed missing import.
Added immutable locked state snapshots and receive-age expiration; bridge uses
the watchdog. New ROS parameter state_max_age_sec defaults to 2 seconds. Expired
state blocks takeoff and cannot suppress emergency landing. Clock anomalies
revoke remembered state. Full suite: 352 passed. This is a new live state guard;
SITL timing and ROS adapter behavior remain to be validated.

No git commands, network/ access, ROS launches or hardware operations performed.

## Further P0/P1 batches (2026-11-09)

3. Malformed clock/container tests failed first (five failures, one error). Reject
   malformed times; repeated timestamps cannot confirm; gaps >= hold_after reset
   debounce. Two fists still bypass debounce. Mocked landmark-to-service chain:
   360 passed.
4. Actual bridge loaded with inert ROS doubles: request fields, missing service,
   rejection/exception, timeout, FAIL ack. 365 passed.
5. Invalid ratio/altitude tests failed first. ROS YAML startup thresholds, camera
   model confidence, timeouts and altitude added. Defaults preserved except FC age
   guard; no dynamic reconfiguration. 367 passed.
6. Board/systemd templates never enabled/executed; SITL-only control guard, camera
   flock, healthcheck, journal capture. Sourced board/UART/ELRS/calibration/failsafe/
   hover/tether guide. PCB identity still unverified. 367 passed after each batch.
7. Test-first opt-in 3D joint-angle classifier and calibration; orientation,
   ambiguity, invalid pose and overlapping labels. Not live; confidence is a margin
   score, not probability. 372 passed.
8. Video regressions failed first: cleanup on bind failure, unsupported host option,
   invalid fps. Fixed; standalone all-interface default retained, board uses
   loopback. Camera/socket mocked. 375 passed.
9. Service-wait cancellation regression failed first. Recheck takeoff epoch and
   fresh state just before request submission. Already-sent calls cannot be
   recalled. 377 passed.
10. Overlapping landing/hold and new takeoff regression failed first. Active-safety
    counter rejects overlapping takeoff. No physical touchdown latch. 378 passed.

## 2026-11-09: admission, transition and adapter red-team batches

11. Added command-admission tests before implementation (missing module failure).
    Three bounded lanes, no queued commands, reserved landing capacity, stale lease
    release protection; 10,000 duplicate attempts remain bounded. 381 passed.
12. Reproduced unscheduled old takeoff after safety (missing ticket API failure),
    added epoch tickets. Reproduced older hold overriding landing, added stale-hold
    rejection/landing-in-progress guard. Full suites: 382 then 383 passed.
13. Camera/inference exceptions reproduced as two errors; now treated as missing
    input, with throttled generic diagnostics. Native blocking still unresolved.
    386 passed.
14. Shutdown during service wait and late ACK tests failed first. Stop event blocks
    later submissions and response waits; pending takeoff invalidated. 388 passed.
15. Scenario contracts written first (missing module). Added five transport-neutral
    plans, mock runner, plan-only Bash wrapper and acceptance semantics. 393 passed.
    No real SITL/RC-loss injection executed; no physics claim.
16. Live-script tests failed before ROS import refactor. Explicit --sitl-isolated
    gate, fresh connected/disarmed initial state, bounded ACK history and matching
    command parser. Attestation cannot detect hardware. 396 passed.
17. Unconfirmed GUIDED/arm tests failed first; bridge now waits for actual fresh FC
    transitions (5 s startup-configured timeout). Adapter delayed/timeout/revocation
    tests added. 401 passed. Live test ACK wait extended from 5 to 45 s to cover
    default service/transition sequence; this is test timing, not FC failsafe.
18. Latency ledger tests failed missing module, then bounded statistics implemented.
    Offline only; provisional budgets and held-out gesture campaign documented.
    405 passed.
19. Pilot mode change/disarm before request tests failed first. Recheck GUIDED
    before arm/takeoff and armed=true before takeoff send. 407 passed.
20. Camera cleanup failures reproduced first; nested cleanup and ROS shutdown
    finally blocks. Startup model/timer leaks reproduced and fixed. Full suites:
    409 then 411 passed. Bash setup sourcing now permits optional unset variables;
    Bash not installed here, so scripts remain unexecuted.
21. Added core audit/backlog separating tested logic from unfinished target work.
    More than 20 substantive remaining P0/P1 tasks; list is not exhausted.
    411 passed after documentation batch.
22. Stale preview frames/reversed clock tests failed first. Frames expire at 2 s
    default (--frame-max-age); /healthz returns 503 for stale/unavailable capture.
    Receive/dequeue freshness is not exposure age. 413 passed.
23. Extreme altitude/ratio configuration regressions failed first. Prototype altitude
    now requires (0,2] m; curl ratio (1,3]. Defaults 2 m and 1.1 unchanged. Expanding
    beyond this prototype envelope requires a reviewed code change. 413 passed.
24. Joined actual gesture and bridge adapters in memory with inert CV/ROS clients,
    inline workers, actual policy/controller/watchdog/admission. Verified complete
    publication/service/observed-state/ACK chain and camera-loss hold/land.
    414 passed; no real middleware or flight dynamics.
25. Preview duplicate-classifier/startup cleanup tests failed first. Preview now
    imports the live pure classifier and releases resources on errors. Fixed a
    Windows console Unicode failure in camera-unavailable message. Removed the
    unsupported front/back accuracy claim from classifier header. 417 passed.

Last observed timestamp: 2026-11-09 07:55 UTC before final preview batch. No
multi-hour duration or completed-drone claim is made from this checkpoint.

## Further P0/P1 acceptance work

26. Test-first SITL observation contract: fresh disarmed/on-ground, observed target
    altitude/in-air, LOITER position/altitude dwell with distinct samples, and
    landed/disarmed. Missing-module failure first; 425 passed after implementation.
27. Red-team observation regressions: RC mode before injection and unobserved gap
    incorrectly accepted. Mark acknowledged injection and require later state;
    reset hold dwell on global and individual stream gaps. Full suites 427/434
    passed after fixes (one later position-gap counterexample was isolated first).
28. Guarded real-ROS SITL runner implemented, never executed here. Defaults plan-only;
    explicit execution/isolation/endpoint flags, extra RC-fault flag, simulator-only
    parameter refusal gate, one publisher/subscriber, observed outcomes. Uses
    official ROS MAVROS ParamSetV2 and SIM_RC_FAIL documentation. Only explicit
    RC-loss changes SIM_RC_FAIL 1 then restores 0; does not edit FC failsafes.
    CLI/restore/mutation tests failed first; 431 passed. Scenario/restore exception
    regressions failed first; cleanup/failure report fixed, 433 passed.
29. LOITER submission after a newer landing during service wait failed first.
    Added hold epoch permission recheck before submission. 435 passed.
30. Added real-thread pending-response cancellation and all service-boundary safety
    interleavings; no hardware or ROS. 438 passed. Already-sent calls still cannot
    be recalled and landing completion is not latched.
31. Pending-arm/disarmed snapshot skip regression failed first. Hold/landing no
    longer skip due to disarmed state while a takeoff sequence is active. This
    attempts safety service despite stale pre-arm snapshot; it cannot guarantee
    FC ordering of already-sent requests. 439 passed.
32. APJ artifact tests first (missing module); read-only board-ID, bounded zlib,
    duplicate-key, image-size and optional trusted SHA256 checks. No downloads,
    flashing, signature verification or physical-board inference. 446 passed.
33. Updated SITL/bring-up/backlog docs and manually ran plan-only hold and inert
    mock RC-loss CLIs. Both exit 0, explicitly no simulator validation. Full
    portable suite after documentation batch: 446 passed.


## Recovery checkpoint, concurrent-writer observation (2026-11-09)

Read AGENTS.md, SAFETY.md, FINAL_REPORT.md, STATUS.md and LOG.md. Inspected recent
src/tests/core docs. Initial full portable suite: 540 tests, exit 0. While reading,
source changed externally: duplicate bridge tail disappeared and profile/budget/
heartbeat work arrived. Asked user about another active session; did not kill
processes or overwrite those source changes. Later full suites passed 545, 547
and 552 tests as concurrent tests arrived. Do not attribute those other additions
to this recovery session or regard this as an immutable source snapshot.

This session added RECOVERY_ACCEPTANCE.md (beginner staged bench, simulator,
human-only props-off motor, engineered tether and pilot-hover gates with stop
conditions) and ORANGE_PI_MEASUREMENT.md (measurement-led tuning, bounded camera
parameters, latency/thermal evidence and explicit unmeasured target limits).
Added AST recovery regressions for shadowed definitions and accidental nested
adapter methods; all current source scopes pass. No claim that syntax checks
alone detect every interrupted edit.

Red-team reproduced doctor false pass for connected:true plus armed:false and
armed:true. Fixed isolated read-only state parser to reject duplicate, malformed,
missing and oversized fields. Three new regressions plus existing doctor tests
pass. This tightens a diagnostic gate; no flight parameter or actuation changed.
Added 28 acceptance follow-ups to BACKLOG.md and immediately completed R01/R02.
Full suite after this implementation: 552 tests, OK, exit 0; schema CLI PASS.

No git commands or network/ access, external source retrieval,
ROS/camera/FC execution, motor arming or service installation. Windows portable
mock checks only. Concurrent source writes limit checkpoint reproducibility.


Recovery continuation: added per-row missing/duplicate landmark CSV mutations
and a seeded 2,000-frame actual-policy/fake-FC post-emergency campaign. No arm,
takeoff or GUIDED service after latch in these samples. Full suite 556 passed,
exit 0. R25 has initial mutation coverage; broader resource/corpus acceptance is
still pending. Rewrote FINAL_REPORT.md to reconcile older 446-test/no-latch claims
with current implementation and explicitly disclose concurrent-writer limits.

Final observed verification: 558 tests passed, exit 0 (concurrent additions continued). No failing cases. Source ownership remains unresolved; further overlapping edits deferred.

## Continuation after recovery checkpoint

Latest primary-agent full suite before sustained campaign: 815 passed, exit 0.
Batch 51 final-state-read cancellation regressions passed (814 cases before the
stress harness test was added). No external submission atomicity claim.

Batch 52: added tools/stress_core.py with independently modeled landing latch,
random commands/service failures/freshness/reset attempts, rigid image transforms,
malformed points and real-thread service-boundary interruptions. Seeded short
campaign plus full suite pass. Started an explicit two-hour campaign, seed
20261109, with periodic SHA256 drift checks of seven core sources. Source edits
to those seven files are avoided during the campaign. No ROS/camera/FC/network
interfaces imported or opened by this campaign; no physical actuation.

Batch 53 in progress: continue recovery R04, rejecting split/multiple/nested ROS
state documents in doctor while retaining the prior contradictory-field tests.

Batch 53 completed: full suite 816 passed. Parser is a restricted known-state
subset, not arbitrary YAML or source freshness evidence. Continued R06 with exact
ROS type checks for the three core topics and four FC services. All probe arrays
are read-only; no service invocation or publication. New wrong-type regressions.

Batch 54: full suite 817 passed after doctor type checks. Added
tools/verify_portable.py to run tests between deterministic SHA256 manifests of
src/tests/tools/board and SITL scripts/config. Forbidden roots are never searched.
It detects endpoint drift, not transient edits restored between hashes or an
immutable snapshot. Stop other writers for target acceptance. Manifest self-test
added; full suite rerun follows. This continues R27 without claiming it complete.

Batch 54 result: 818 tests passed, exit 0, 219-file before/after manifest unchanged
(digest ac5922c7ddcefd9824229ee3e751ea55b47de8a2969e58029b081a13be634dbf).
Reconciled STATUS.md and rewrote FINAL_REPORT.md with current behavior, untested
boundaries and exact board/SITL human commands. Stress result remains provisional
until its requested two-hour deadline; no completed duration is claimed yet.

Batch 55 in progress: world-hand order/count adversarial tests. Aggregate mixed-
hand/two-fist decisions must not depend on image/world ordering. This does not
prove correct physical handedness, user identity or occluded landmark estimates.

Batch 55 result: 820 tests passed, exit 0. Existing documentation-only batch also
passed the full 818-case suite before the two new hand-order cases were discovered.

Batch 56 in progress: explicit FCU launch endpoint required, removing automatic
selection of /dev/ttyUSB0:921600 when omitted. GCS forwarding/target IDs unchanged.
Disclosed routing-selection behavior change before editing; actual launch tested
with inert launch API doubles only. No MAVROS process or FC connection started.

Batch 56 result: 821 tests passed. Batch 57: legacy live integration script now
requires explicit isolated UDP endpoint, fails fast on missing/failed/mismatched
ACK, requires single command/state publishers, verifies post-landing inhibition,
and always cleans up ROS/node after scenario errors. Retains the explicit
simulator duplicate-command checks after confirmed initial acceptance, with no
blind flight retry. Replaced misleading flight/altitude docstring with actual
ACK/armed limitations. Three inert regressions added; live script not executed.

Manifest scope extended to standalone preview/video/live-test/viewer source files;
reject top-level source-root symlinks before traversal. No forbidden roots read.

Batch 57 regression run caught six import errors after a docstring replacement
left old text unquoted. Corrected the replacement at the future-import boundary;
no live script was run. Passing rerun result follows below. The sustained core
campaign's seven tracked source files were unchanged and its assertions continued.

Batch 58: offline calibration CLI refuses fewer than five distinct world poses
per class, preventing identical frozen/replayed frames from satisfying its minimum.
Coordinate variation does not prove independent exposure; held-out evidence still
required. Added capture-quality regressions. No recordings or user profiles made.

Batch 57 passing correction: 824 tests, exit 0, 226-file manifest unchanged
(e6253743f75e15036942bd3d3aca1835187a5132ac12f448b8b3e547be756da6).
Batch 58 initially had two test-fixture context-manager errors (Mock vs MagicMock),
corrected the fixture; full suite 826 passed, exit 0.

Batch 59: reviewed tagged MAVROS 2.14.0 command/parameter sources and upstream
plugin-config regression report. Documented backend mutually-exclusive command
callbacks and ACK timeout, cached parameter getter and required installed-package
readbacks in MAVROS_CONTRACTS.md. Local landing admission is not backend priority.
No MAVROS/FC parameter or runtime changed. Updated audit/report stale boundaries.

Batch 60: actual CSV fixture now passes through actual gesture timer and bridge
construction/callback/service code with inert ROS/CV clients, explicit startup
dwell/reset, heartbeat, observed GUIDED/armed updates, ACK and post-land inhibition.
This complements the transport-free harness and includes the startup gate that
older __new__ fixtures bypassed. No actual camera/ROS/FC used. CSV decoder now
turns strict-format/oversized-field csv.Error into bounded ValueError diagnostics;
large-field/unclosed-quote regressions added. Full suite rerun follows.

Batch 61: restricted doctor ROS-state scalar validation rejects list/tag/null
shapes in mode/frame_id and out-of-range stamp seconds; simple quoted/plain ROS
strings remain accepted. Conservative known-state grammar, no general YAML or
source-time freshness claim. Additional malformed-output regression added.

Batch 60 result: 828 passed. Batch 61 result: 829 passed, exit 0. Updated status
with actual-adapter CSV evidence and current campaign checkpoint. Added concrete
follow-ups R29..R34 from source review. These are not hidden as passing-test claims.
Tracked core files remain frozen during the sustained campaign; fixes affecting
them require separately recorded validation after that campaign completes.

Batch 62: manifest-wrapped suite 829 passed, 228 files unchanged, digest
a05828c870f35e08fef59e563da545a49136ab7813735123d7ee4bf2bb1dbfac.
Prepared pure canonical command/ACK framing and 10,000 malformed-string checks
after observing unknown payload reflection can resemble a recognized ACK prefix.
Helper rejects unknown labels, prevents control/newline records and bounds detail.
Live integration is queued for after the tracked-source campaign; it is not yet
a live safeguard and does not supply authentication or request IDs.

Batch 62 result: 833 tests passed. Batch 63: reviewed official rclpy Jazzy client
source: remove_pending_request releases local correlation, not FC execution.
Prepared a pure wait_response helper with deadline/stop/clock checks and cleanup
on abandonment, plus timeout/late-completion/cleanup-failure regressions. Live
adapter integration remains queued until the tracked-source campaign finishes;
do not claim local future cleanup in a running bridge from this helper alone.

Extended the prepared future helper with a bounded poll count for frozen clocks
and rejection of unrepresentable deadlines. Existing live service adapter remains
unchanged until campaign completion; all new helpers are clearly separated from
live claims. Positive/negative future paths and clock faults are unit tested.

Batch 64: independent integer-tick reset reference model across 18 combinations
of receive intervals and dwell bounds (1/5/60 s); cached polling cannot stand in
for source progress, and gaps >=2 s prohibit dwell. This extends the three initial
freshness counterexamples without ROS. Identified R36: a reset must not permit
new takeoff through a known-open/unavailable landing path. Queue bridge integration
with R29/R30/R31/R35 after the timed core campaign, then rerun the complete suite.

Batch 64 result: 839 tests passed. Batch 65: added camera-only world CSV recorder,
plan-only unless --capture, with external/new-file-only destination, distinct
one-hand metric samples, sample/attempt/time/frame-budget bounds and negotiated
camera checks. No images/ROS/FC calls. Four inert capture tests passed in full
843-case suite. Added CLI plan/startup-cleanup/source-output refusal regressions
and human-only board capture commands; rerun follows. No actual camera opened.

Batch 65 completed: 846 tests passed, exit 0. Clarified source-reviewed incoming
heartbeat/state publication and rclpy local pending cleanup contracts, while
retaining target runtime/frequency uncertainty. Updated status with campaign
checkpoint and explicit prepared-but-not-live helper limits.

Batch 66: clarified optional pose live-path and default 2D preview documentation.
Actual gesture callback regression shows continuous 300 ms two-fist frames are
rejected as stale but cannot indefinitely renew input: hold then land by 5.4 s
on the deterministic sample grid. This does not promise immediate emergency from
over-budget frames or true camera exposure freshness. R12 initial portable
acceptance complete; no hardware action. Full suite rerun follows.

Batch 67: added the missing reset-eligible abstract state to the generated table:
70 controller command cells now include every command after dwell is complete,
not just a dedicated reset example. Land restarts dwell; open palm/hold still
block until explicit reset. 240 service-adapter cells remain unchanged. Full
portable suite rerun follows; tracked core sources untouched during campaign.

Batch 66 passed 847 tests; batch 67 passed 857 tests, exit 0. Campaign checkpoint
3,821.4 s: 1,093,873 cases, 109,387,300 commands, 4,375,492 geometry checks and
21,878 thread trials, no assertion or seven-source drift. Progress reports jumped
from 3,180 to 3,761.4 seconds; cause unverified. Record elapsed campaign evidence,
not uninterrupted CPU load or a target timing bound. No deliberate sleep was
inserted in the campaign to reach its duration; it continuously attempts cases
subject to host/process scheduling and reporting.

Batch 68: replaced stale launch docstring instructions about the former physical
placeholder with the explicit-endpoint contract and current bring-up reference.
No further routing/default behavior changed. Tagged upstream apm.launch argument
names were reviewed; installed launch/front-end behavior remains unexecuted.

Batch 69: bounded diagnostic probe now reaps its owned child if reader-thread
creation fails, avoids joining an unstarted thread, and tolerates process-exit
cleanup races. Harmless local Python-child regression verifies exit/closed pipe;
no ROS/camera/FC or unrelated process is touched. Complete suite rerun follows.

Batch 70: calibration CLI now refuses profile output inside source and requires
explicit --replace-profile before replacing an observed existing destination;
samples are not read on forbidden output. Pure save_profile API still supports
atomic replacement for deliberate programmatic updates. Updated beginner command
paths to external capture directory and documented absolute YAML profile paths.
No profile/data files were created by this agent; inert regression added.

Batch 70 result: 859 tests passed. Batch 71: camera recorder completes cleanup
before persisting data or printing success; cleanup failure closes the other
resource and returns failure without writing a dataset. Inert cleanup fault
regression added. No actual recording, image or camera access took place.

Batch 71 result: 860 tests passed, exit 0. Batch 72: 640 generated composite
bridge-entry subcases across every admission lease subset, FC connectivity/arming
category, latch and command category. Independent expected traces, lease-release
checks and post-land takeoff inhibition complement the 70 command and 240
primitive cells. Existing leases represent admitted pending workers, not all
active thread schedules. Full portable suite rerun follows.

Batch 72 result: 861 tests passed. Batch 73: added a locked admission-idle query
that includes workers admitted but not yet started; lifecycle assertions verify
all lanes must release. Public reset integration queued after campaign. Also
recorded R38: avoid reopening a state-read window after final mode/armed check;
use the same immutable snapshot with an epoch check. No native call is made
atomic or cancellable by those local guards.
