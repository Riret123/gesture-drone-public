# Command-state contract

This table is an abstraction of the controller, not a proof of FC execution.
All 70 cells are generated as independently expected service traces by
tests/test_landing_latch.py. Another 240 cells in test_bridge_primitive_matrix.py
cover all five primitive requests, six mode values, connected/disconnected,
armed/disarmed and latched/unlatched combinations. Mode transitions, active-worker guards and adapter
submission races additionally have boundary/thread tests. It is not an exhaustive
model of middleware, pilot actions, firmware, or all possible thread schedules.

test_command_composite_matrix.py additionally exercises 640 combined bridge-entry
subcases: all eight takeoff/hold/land lease subsets x five FC categories
(unknown plus connected/disconnected and armed/disarmed) x latch boolean x eight
command categories. Its independent expected service traces also verify leases
are released and landing reception inhibits later takeoff even when admission is
busy. Existing leases model admitted, not-yet-started workers; active thread
interleavings are exercised separately. This explicit abstraction does not
replace FC/executor scheduling evidence or claim an infinite-state proof.

| State | open_palm | fist / land / emergency | hold | operator_reset | other / arm / takeoff / empty / unknown |
|---|---|---|---|---|---|
| Connected disarmed, unlatched | GUIDED, arm, takeoff | Latch; skip service | Skip service | Fail until dwell | No action |
| Connected armed, unlatched | GUIDED, skip arm, takeoff | Latch; request land | LOITER | Fail | No action |
| Disconnected, unlatched | Fail | Latch; attempt land | Attempt LOITER | Fail | No action |
| Unknown FC, unlatched | Fail | Latch; attempt land | Attempt LOITER | Fail | No action |
| Connected disarmed, latched | Fail | Retain latch; skip service | Fail | Clear only after dwell and idle workers | No action |
| Connected armed, latched | Fail | Retain latch; request land | Fail | Fail | No action |
| Connected disarmed, latched, dwell complete, idle | Fail until explicit reset | Retain latch; restart dwell; skip service | Fail | Clear latch | No action |

Landing always invalidates takeoff epochs. Safety reception latches before worker
admission; failed/busy service cannot clear it. Landing during arm submission may
still race an already-sent FC request; no Python lock can recall that request.

Hold invalidates pending takeoff but does not latch. A newer landing invalidates
an older hold's epoch and prohibits LOITER. Duplicate in-progress takeoff/landing
requests skip without queues. Active safety workers prohibit new takeoff. Shutdown
invalidates pending takeoff and prohibits later adapter submission/ACK publication.

Reset requires the explicit `operator_reset` command, connected/disarmed
observations for five seconds, and no active safety/takeoff/landing worker.
Invalid/reversed clock, armed/disconnected state and observation gaps >=2 seconds
erase reset progress. A new landing erases previous dwell. This command is an
operator confirmation convention on an unauthenticated string topic, not access
control. Never expose that topic to untrusted publishers. The latch is in memory
and is lost on process restart; the live adapter therefore always starts latched.
Every launch needs the observed dwell and explicit operator reset. Pure offline
controller callers can opt into startup_latched; fake harnesses default unlatched.

Each service/mode gets at most three failed submissions per process. Failures are
cumulative, not necessarily consecutive; success does not erase uncertain prior
effects. Zero automatic retries or half-open actuation probes. Restart recovery
must first resolve uncertain vehicle state; restarting to defeat a guard is unsafe.
