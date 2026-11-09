# Round 03 brainstorm: QA and QA red team

Scoring uses S/T/P/E (risk reduction, testability, portfolio clarity, effort),
0–3 each. Test campaigns count only when executable or tied to a concrete review.

| ID | QA idea and independent oracle | S/T/P/E | Vote |
| --- | --- | --- | --- |
| Q3-I1 | Continuous crossing campaign: analytic 90-degree collision, head-on, parallel, stationary and delayed paths. | 3/3/3/3 | 12 |
| Q3-I2 | Semantic digest mutation campaign: equivalent numeric representations same digest, changed point different digest. | 3/3/3/3 | 12 |
| Q3-I3 | Log-scale numerical generator: subnormal, ulp neighbors and near-boundary values. | 3/3/2/2 | 10 |
| Q3-I4 | In-memory ROS-shaped harness oracle: scripted delayed service completion without ROS imports. | 3/3/3/2 | 11 |
| Q3-I5 | Acceptance evidence index: distinguish test methods, cases, docs, live and blocked evidence automatically. | 2/3/2/2 | 9 |

| ID | QA red-team idea and risk exposed | S/T/P/E | Vote |
| --- | --- | --- | --- |
| QR3-I1 | Mutation oracle challenge: deliberately remove threshold check and confirm selected regression fails. | 3/3/3/2 | 11 |
| QR3-I2 | Dense-vs-analytic separation oracle: analytic minimum must be <= dense observed minimum. | 3/3/3/2 | 11 |
| QR3-I3 | Metamorphic invariance: translating both paths or swapping labels preserves separation. | 3/3/3/3 | 12 |
| QR3-I4 | Late/out-of-order service responses: acknowledgements must not be confused with completed state. | 3/3/3/2 | 11 |
| QR3-I5 | Evidence honesty check: source-only tests cannot close installed/physical validation blockers. | 3/3/2/3 | 11 |

Selected Q3-I1 and Q3-I2 for this round, with QR3-I2/I3 checks alongside. Mutation
testing and delayed service responses are deferred, not silently marked complete.
The cross-role vote favors origin binding first, then continuous separation.
