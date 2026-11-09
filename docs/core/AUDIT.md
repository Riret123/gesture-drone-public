# Core audit and red-team record

Current continuation overrides historical rows below: landing/startup inhibition,
explicit reset, same-host heartbeat supervision, opt-in saved 3D profiles and
returned-frame budgets are implemented. Latest evidence is in LOG.md/STATUS.md.
Sixty command cells plus 240 primitive-adapter cells pass; they are finite models,
not exhaustive ROS/FC proofs. Native/FC submission ordering remains unresolved.
MAVROS_CONTRACTS.md explains why local reserved landing capacity cannot establish
priority through a mutually-exclusive backend command group.

| Boundary | Evidence | Remaining limits |
| --- | --- | --- |
| classifier/policy | malformed geometry/clocks, repeated timestamps, sampling gaps, emergency | image age and camera accuracy unknown |
| gesture adapter | actual code with inert camera/inference; runtime/startup/cleanup faults | real camera/MediaPipe/executor untested |
| flight logic | ordering, rejection, cancellation, overlap, delayed workers, confirmation | service acceptance is not completed flight |
| bridge adapter | actual requests with inert ROS; wait/response/transition/shutdown faults | real middleware/concurrent service ordering untested |
| state watchdog | immutable snapshot, expiry boundary, clock reversal, malformed input | receive time is not source freshness |
| worker admission | 10,000 duplicate attempts, reserved landing, stale release | process scheduling/ROS transport not modeled |
| live test script | no-flag refusal without ROS, ACK parsing/matching, fresh initial state | no altitude check or request IDs; not run live |
| video server | host/CLI checks and bind cleanup mocked | capture stalls/stale frames unresolved |
| launch wrapper | source/placeholder review and serial mapping docs | installed MAVROS launch untested |
| preview/keyboard/CLI | source/interface review and existing tests retained | duplicate preview logic and publisher isolation |
| pose features/latency | synthetic orientation/calibration and bounded statistics | offline, no measured efficacy |
| other existing modules | existing full regression suite retained | fresh exhaustive behavior audit still pending |

Red-team counterexamples fixed: NaN/collapsed hand becomes fist; disconnect during
takeoff; old disarmed state suppresses landing; repeated times confirm gesture;
old samples survive a gap; cancellation during service wait; overlapping takeoff
and safety; delayed old takeoff/hold after newer safety; unbounded worker spawning;
late work during shutdown; returned camera/inference failures bypass loss policy;
startup/cleanup leaks; mode_sent mistaken for observed GUIDED; pilot mode change
or disarm before final submission. Tests were written before corresponding fixes.

Residual attacks: already-sent requests may execute after emergency; concurrently
sent hold/land requests can arrive out of order; landing is not latched through
touchdown; failed landing has no automatic retry; old buffered camera exposures
appear fresh; native stalls stop gesture timers; unrelated publishers can inject
commands; repeated same-command ACKs lack identity; companion process death may
leave a MAVROS heartbeat alive. These need further design and real SITL evidence.
