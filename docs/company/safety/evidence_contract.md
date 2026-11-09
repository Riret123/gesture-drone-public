# R02 S01 - evidence metadata contract
`sensor_evidence` defines explicit requirements: key, scope, configuration revision, max local age and accepted origin types. Records include origin, observation time, opaque audit reference and strict boolean result. Unexpected/duplicate keys, wrong scope/revision, unaccepted origin, stale/future time, missing reference and invalid/failed result create findings.

A report says METADATA_COMPLETE or INCOMPLETE; never SAFE, READY or AUTHORIZED. It does not fetch a reference, authenticate a person, measure hardware or issue commands. Empty requirements reject rather than produce a vacuous pass.

A human attestation cannot substitute where a requirement accepts measurement only. Accepted origins are explicit per requirement, so simulation cannot silently stand in for hardware measurement.
