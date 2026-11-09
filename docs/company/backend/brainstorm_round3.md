# Round 03 brainstorm: backend and backend red team

Use shared S/T/P/E 0–3 criteria from the architect brainstorm. These are effort
and risk judgments; measured performance and user demand remain unverified.

| ID | Backend idea and scoped result | S/T/P/E | Vote |
| --- | --- | --- | --- |
| B3-I1 | Pairwise analytic path separation: return minimum distance/time, not control commands. | 3/3/3/2 | 11 |
| B3-I2 | Immutable mission binding: SHA-256 semantic identifier plus caller-established origin/revision. | 3/3/3/3 | 12 |
| B3-I3 | Event-driven service mock: reproducible request, accept, timeout and late-result traces. | 3/3/3/2 | 11 |
| B3-I4 | Simulator report validator: refuse nonfinite/contradictory summary and timeline payloads. | 2/3/2/3 | 10 |
| B3-I5 | Mission energy estimate adapter: connect durations to measured load assumptions, never invent pack data. | 3/2/3/1 | 9 |

| ID | Backend red-team proposal and adversarial value | S/T/P/E | Vote |
| --- | --- | --- | --- |
| BR3-I1 | Crossing between coarse ticks: two safe endpoints can conceal a collision. | 3/3/3/3 | 12 |
| BR3-I2 | Co-location at launch/end: stationary pre/post paths must participate in comparisons. | 3/3/2/3 | 11 |
| BR3-I3 | Near-parallel velocity subtraction: compare against an independent dense oracle with error tolerance. | 3/3/3/2 | 11 |
| BR3-I4 | Duplicate agent IDs and missing members: fleet registry must reject ambiguity. | 3/3/2/3 | 11 |
| BR3-I5 | Delayed starts and epoch mismatch: explicit global simulation epoch and finite horizon. | 3/3/2/2 | 10 |

Selected B3-I2 and B3-I1. B3-I3 is queued for a later review round; it must not be
counted as implemented now. Report validation and measured energy await stable
output/measurement contracts. Red-team ideas become explicit regression cases.
