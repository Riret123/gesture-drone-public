# Architect red team: round 1

| ID | Attack and evidence needed | State | Owner/fix target |
|---|---|---|---|
| A-R01-1 | ENU home is described but not machine-identifiable; a copied route could use another origin. Require explicit future mission-origin metadata or a documented adapter refusal. | open | Architect round 2 |
| A-R01-2 | Convex fence does not imply obstacle clearance. Ensure simulator report names missing obstacle model and avoids safe-flight wording. | open | Architect round 2 |
| A-R01-3 | Canonical export may exceed ingestion byte bound at maximum plan size. Check 256 longest names and maximal numeric precision. | open | Backend round 2 |
| A-R01-4 | Per-point dwell cap permits 256 hours total. Add explicit mission-duration budget before simulation allocates samples. | open | Backend round 2 |
| A-R01-5 | Frozen tuples protect normal mutation but not object.__setattr__; no security boundary against malicious Python code. State process trust model explicitly. | open | Architect round 2 |

This is an adversarial review pass by the assigned workstream agent, not a claim
that a separate human or 20 simultaneous agents reviewed the code.
