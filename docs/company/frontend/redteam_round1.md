# Frontend red team — round 1

Separate adversarial review pass of the frontend artifacts. Findings retain their
IDs across rounds. Fixed means the stated narrow regression is covered, not that
the entire threat is eliminated.

| ID | Attack | State | Evidence / next action |
| --- | --- | --- | --- |
| FE01 | bool battery looks like 1 percent | fixed | test_strict_fields_and_boolean_numbers |
| FE02 | source age 1 + local delay 1 accepted at limit 2 | fixed | test_source_and_transport_age_add |
| FE03 | mutate input history after normalization | fixed | test_history_snapshot_does_not_alias |
| FE04 | unknown schema field hides command payload | fixed | test_unknown_and_missing_fields |
| FE05 | forged receive timestamp makes packet fresh | open | local adapter must own timestamp; no authentication claim |
| FE06 | huge Python integer crashes math.isfinite | open | reproduce and harden numeric helper next round |
| FE07 | raw JSON duplicate keys disappear before validation | open | bounded strict decoder needed next round |
| FE08 | browser ignores helper and accepts weaker schema | open | versioned browser adapter integration and tests |
| FE09 | source repeats old packet with fresh age | open | session/sequence gate and honest-source limitation |

Round 2 priority: FE06 and FE07 are executable boundary failures; implement
tests before fixes. FE05 and FE09 need explicit receive ownership and replay model.
FE08 must not be described as fixed by Python-only normalizer tests.
