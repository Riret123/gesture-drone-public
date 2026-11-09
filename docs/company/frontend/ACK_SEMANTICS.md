# Acknowledgement UX

Display a service result with the word "accepted" or "rejected" and its source.
Never translate OK into "airborne", "landed" or "safe". The live bridge observes
service completion, not the physical outcome of a maneuver. A timeout is ambiguous:
the FC may have executed an already sent request even if no response arrived.

A future correlated record should include session ID, command ID, receipt time,
service name, result category and evidence source. A retry must get a new ID and
must not overwrite the earlier ambiguous result. These fields are a proposed
offline contract, not features already present in `/flight_cmd_ack`.

Acceptance scenarios: delayed accept after timeout; repeated no-op; out-of-order
result; disconnect between request and result; unexpected source; malicious text.
Until correlation exists the UI should expose raw bounded text with its limits.
