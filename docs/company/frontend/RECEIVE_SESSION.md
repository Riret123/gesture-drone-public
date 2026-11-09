# Receive-owned telemetry session experiment

`TelemetrySession` establishes a single caller-identified session and owns receive
time from each receive call's local clock. It rejects nonincreasing sequence
numbers, wrong session IDs, malformed snapshots and reversed clocks. No rejected
packet renews receive age. An invalid packet clears the visible sample rather
than showing old positive values alongside INVALID.

Sequence numbers are bounded integers 0 through 2^63-1, excluding bool. No wrap
or implicit restart is accepted. Reconnect requires constructing a new instance
after the adapter independently establishes the new session. The Python class
cannot authenticate that establishment or prevent callers forging inputs.

Tests: receive/stale boundary, duplicate invalidation, invalid packet not consuming
sequence, wrong IDs/bool sequence, reverse-clock clearing, mutation isolation,
source age preservation, new-session replacement, invalid identifiers and decoder
configuration consistency. This is an offline read-only model, not a ROS receiver.
