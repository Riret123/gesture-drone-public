# QA red team: round 1

| ID | Attack | State | Needed evidence |
|---|---|---|---|
| Q-R01-1 | Only minimum examples, no 256-point success case. A fence/name bug could reject all larger missions. | open | max-count valid roundtrip |
| Q-R01-2 | File has no standalone import path bootstrap; suite runner supplies it. Confirm test invocation is documented and avoid claiming plain root discovery succeeds. | open | documented runner; focused runner command |
| Q-R01-3 | One method with many subcases is not many independent tests. Report method count and state numeric mutations separately. | mitigated | baseline explicitly counts methods |
| Q-R01-4 | No randomized valid inputs or independent geometric oracle. Add seeded generation and Euclidean expected distances in simulator tests. | open | round 2 |
| Q-R01-5 | Passing source tests does not prove installed package contains new modules. Keep colcon/install validation blocked in dashboard and handoff. | open | target Linux evidence unavailable |
