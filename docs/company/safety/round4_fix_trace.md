# R04 S04 - safety prior attack fixes
S19 evidence clock rewind: EvidenceSession now validates/stores monotonic evaluation time before record processing. A previous expired record cannot become complete by a later lower now. test_s19_rewind_cannot_freshen_expired_evidence proves the counterexample.

S13/S20 evidence fabrication remains open: session/origin/reference labels do not authenticate real artifacts. A session report is metadata completeness only, and physical/legal evidence still needs accountable external review.

R04 assist tests reject truthy model attestations and demonstrate that missing prerequisites produce no speed estimate. These are model boundary tests, not measurement or flight evidence.
