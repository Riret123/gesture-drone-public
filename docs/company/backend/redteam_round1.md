# Backend red team: round 1

| ID | Attack and expected regression | State | Fix target |
|---|---|---|---|
| B-R01-1 | Direct Waypoint constructor accepts int while from_json accepts float; equality works but serializers need deterministic roundtrip tests for extreme valid precision. | open | round 2 |
| B-R01-2 | Missing-field error does not identify field. Provide structured path diagnostics if UI needs them, without copying attacker values. | open | deferred UI contract |
| B-R01-3 | JSON under byte limit can be deeply recursive; catch is present but test rejection semantics at several depths and ensure no unexpected OverflowError. | mitigated | depth regression in test_input_limits_and_unicode; expand round 2 |
| B-R01-4 | String numeric input may reach math functions later. Constructor gate currently rejects it; add generated type mutations at every plan-level numeric field. | open | round 2 |
| B-R01-5 | Exported data could include a future unknown schema field yet parse silently if defaults added carelessly. Add exact output-key regression. | open | round 2 |

No change to live flight safety parameters proposed in this batch.
