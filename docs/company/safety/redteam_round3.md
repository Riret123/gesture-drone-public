# Safety red team - round 3
| ID | Attack | Status/evidence | Next round |
| --- | --- | --- | --- |
| S15 | Same local timestamp from another boot looks fresh | fixed metadata; test_s14_cross_reboot_monotonic_evidence_rejects | session authenticity external |
| S16 | Caller clears requirement list after session creation | fixed; test_input_policy_list_mutation_cannot_remove_requirements | nested values are frozen records |
| S17 | Matching session bypasses stale evidence | fixed; test_matching_session_still_requires_record_policy | persistent audit not modeled |
| S18 | Invalid envelope hides missing required record | fixed; test_invalid_envelope_cannot_hide_missing_evidence | preserve both findings |
| S19 | Reviewer rewinds now to freshen record | OPEN: EvidenceSession has no last-now state | R04 clock reversal guard |
| S20 | Session string falsely copied from correct boot | OPEN: labels are unauthenticated | human provenance review required |
| S21 | Output metadata-complete represented as gate D authorization | fixed wording only in contracts; cannot control downstream misuse | later claim audit |

R02 S14 is conditionally fixed for honest session identity. R02 S13 fabricated reference remains open; no unit test can authenticate a real-world artifact without a trust system.
