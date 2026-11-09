# QA red team: round 3

| ID | Attack | State | Needed evidence |
| --- | --- | --- | --- |
| Q-R03-1 | Dense oracle is not independent of trajectory lookup. | open | independent closed-form generated linear paths in next campaign |
| Q-R03-2 | Random scenes never reach maximum32-agent valid count. | open | cheap stationary max-fleet pair-count test |
| Q-R03-3 | Tolerance fixes might weaken the conflict threshold silently. | fixed review | only geometric test assertions changed; threshold equality regression retained |
| Q-R03-4 | Benchmark could be quoted as Orange Pi/flight performance. | documentation mitigated | benchmark explicitly environment-specific model analysis |
| Q-R03-5 | No missing-member, timestamp-skew or stale-fleet attack tests. | open | registry contract next round |
| Q-R03-6 | No report-output schema/finite-value validator or byte cap. | open | accepted report contract and bounded serializer |

Remote CI, installed package and all real-world validation blockers remain open.
