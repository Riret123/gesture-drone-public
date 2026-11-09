# Quest input boundary

The existing Quest page is view-only. The offline Deadman helper is not attached
to headset tracking or a command channel. No button in this run enables flight.

A future input adapter must establish a session identity, local monotonic sample
time, bounded sequence number, explicit tracked state, and exact pressed/released
booleans. A tracking interruption must invalidate prior intent. Reacquisition
requires a witnessed release and subsequent press; reconnect must not synthesize
that sequence. Headset sleep, tab suspension and focus loss need independent tests.

Unresolved: physical deadman ergonomics, tracking confidence source, transport
authentication, authority arbitration, FC failsafe interaction and pilot override.
Without those, presenting a green ACTIVE label would misrepresent readiness.

Round 1 acceptance: document the boundary and test telemetry booleans strictly.
Next-round experiment: pure input session replay gate with no ROS dependency.
