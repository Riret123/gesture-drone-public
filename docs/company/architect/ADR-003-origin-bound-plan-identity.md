# ADR 003: explicit origin/revision binding and semantic plan identity

Status: accepted for offline experiments, round 03.

`MissionContext` carries a caller-established origin ID, bounded integer frame
revision and SHA-256 plan ID. `BoundMission` verifies that the digest matches the
mission at construction. `require_context` refuses unbound plans and mismatched
origin or revision. Swarm comparisons require identical origin/revision.

The digest normalizes known numeric fields to floats, with signed zero converted
to +0.0. Integer version remains integer. Point names/order, coordinates/dwell,
speed, envelope, frame and version affect identity. JSON key order, whitespace,
and equivalent int/float spellings do not. This is a project-local semantic
encoding, not a claim to implement a standardized canonical JSON protocol.

SHA-256 here identifies content. It does not authenticate a sender, establish
surveyed position, guarantee freshness or approve navigation. Two callers can
assert the same wrong origin label. Binding prevents ordinary metadata mismatch,
not a lying or miscalibrated caller. Real-world origin acquisition remains open.

Acceptance: equal numeric representations/roundtrips share IDs; modified values
and waypoint order change IDs; forged digest, missing binding, invalid revision,
case-mismatched origin and revision mismatch refuse. Frozen context prevents
ordinary reassignment; trusted-process caveat from ORIGIN_AND_TRUST still applies.
