# R03 V01 - single-frame ambiguity contract
`CandidateFrame` carries one session, sequence, capture time and immutable tuple of detections. `CandidateGate` requires an explicit positive maximum candidate count and rejects oversized frames before inspecting candidates. Exactly one expected tag may be present. Duplicate expected-tag detections reject even with identical poses; no first-wins or highest-confidence shortcut exists.

Other tag IDs may coexist, but all candidates must identify the configured camera/calibration and same receive time. Target absence rejects and does not consume accepted sequence state. The selected target still passes CaptureGate and ObservationGate quality/freshness checks.

This only resolves metadata multiplicity. A detector returning one plausible false tag is still an open perception hazard. The gate is offline and does not feed the live bridge.
