# R03 S01 - session-bound evidence
`EvidenceSession` binds a copied tuple of requirements to one exact session ID. Each SessionEvidence envelope must match that session before its record enters metadata review. A record from another boot with identical local numeric time rejects and also leaves required evidence missing.

Session identity is supplied by trusted experiment setup and is not authentication. It is not automatically inferred from incoming records. Requirement-list mutation by the caller cannot remove stored requirements after construction. Scope/revision/origin/time checks still run after session selection.

Local monotonic metadata still cannot serve as long-term calendar audit evidence. Persistent signed review records require a separate storage/provenance design.
