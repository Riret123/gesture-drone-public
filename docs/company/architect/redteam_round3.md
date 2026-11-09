# Architect red team: round 3

| ID | Attack | State | Evidence/next step |
| --- | --- | --- | --- |
| A-R03-1 | Matching origin labels can both be wrong. | known unresolved physical risk | dedicated test documents limitation; target survey evidence required |
| A-R03-2 | SHA-256 digest could be mistaken for authentication. | documentation mitigated | ADR 003 explicitly denies sender authentication |
| A-R03-3 | Float minimum near threshold can differ by ulps. | open | separate uncertainty/guardband policy, never claim certified clearance |
| A-R03-4 | Fleet list may omit an actual member and report no conflict. | open | expected-member registry + freshness contract next round |
| A-R03-5 | Point-body trajectories ignore rotor/body radius and tracking error. | open | explicit uncertainty inputs and missing-evidence refusal |
| A-R03-6 | Long output may exceed available consumer memory. | open | bounded serialization policy for mission report |

Producer fixes next round must preserve separation between metadata guarantees
and actual surveyed/physical evidence. Do not close A-R03-1 with another label test.
