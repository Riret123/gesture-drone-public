# Round 03 brainstorm: architect and architecture red team

Scoring: safety-risk reduction (S), testability (T), portfolio explanation (P),
effort fit (E), each 0–3; total at most 12. Scores are team judgments, not market
statistics. New means proposed in this company session, not a novel invention.

| ID | Architect idea and rationale | S/T/P/E | Vote |
| --- | --- | --- | --- |
| A3-I1 | Origin/revision-bound mission digest: make coordinate reuse mismatch explicit before multi-agent comparisons. | 3/3/3/3 | 12 |
| A3-I2 | Continuous closest-approach contract: compare piecewise paths between telemetry ticks. | 3/3/3/2 | 11 |
| A3-I3 | Optional obstacle occupancy interface: separate terrain evidence from fence geometry. | 3/2/3/1 | 9 |
| A3-I4 | Versioned command-intent envelope: document source, lease and observation IDs without wiring live transport. | 3/3/2/2 | 10 |
| A3-I5 | Capability manifest for demos: machine-identify mock/simulation/target-verified features. | 2/3/3/2 | 10 |

| ID | Architect red-team proposal and why it attacks the design | S/T/P/E | Vote |
| --- | --- | --- | --- |
| AR3-I1 | Digest equivalence attack: +0/-0 and int/float representations must not change semantic identity. | 3/3/2/3 | 11 |
| AR3-I2 | Conflicting origin labels: demonstrate matching labels cannot prove common surveyed coordinates. | 3/3/2/3 | 11 |
| AR3-I3 | Resource amplification graph: multiply agents × segments × samples to bound worst-case comparison. | 3/3/2/2 | 10 |
| AR3-I4 | Malformed process-object contract: distinguish hostile Python from untrusted JSON in every security claim. | 2/3/2/3 | 10 |
| AR3-I5 | Schema evolution refusal matrix: newer versions, unknown fields and incompatible coordinate axes must refuse. | 3/3/2/3 | 11 |

Top implementation recommendation: A3-I1 paired with AR3-I1, then A3-I2. Explicitly
defer obstacle maps, intent integration and capability catalogs until their input
contracts and acceptance gates are reviewed. No votes imply flight authorization.
