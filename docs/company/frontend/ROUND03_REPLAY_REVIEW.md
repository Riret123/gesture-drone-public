# Round 03 implementation and review record

Selected F03-1/FR03-1: bounded read-only replay analytics and adversarial corpus.
Implemented replay_analysis.py, analyze_replay.py, a four-row synthetic fixture,
15 analyzer/reader tests and six CLI tests. Unicode label defense is shared by
telemetry and analytics, with seven focused regressions. Two Python methods and
one JS case consume a shared 23-vector status corpus; vectors are not counted
as separate unittest methods.

Observed integration failures and corrections:

1. Fixture generation through a Windows shell pipeline replaced literal Unicode.
   The 64-emoji fixture became a longer malformed string and correctly failed.
   Regenerated using ASCII Unicode escapes. Both language consumers now pass.
2. Two new swarm tests expected exact floating crossing time=1. Analytic rounding
   returned 0.9999999999999999; QA used an independent approximate numeric assertion.
   Production separation comparisons and thresholds were not relaxed.
3. Node's child-spawning test mode was blocked by sandbox EPERM. The same built-in
   tests run directly in-process. This limitation is recorded, not called browser QA.

Latest root-observed full suite at 06:28 UTC: 260 passed; after CLI batch: 271.
Other workers continue adding cases, so counts are time-specific snapshots.
Supplemental JS suite: 18 passed, including common contract vectors.

External review: vision/hardware worker independently reviewed telemetry_session
and replay_analysis. It identified generator partial-yield interpretation risk;
CLI regression test_bad_later_row_does_not_emit_partial_report demonstrates that
the complete-report consumer does not print a prefix as a successful result.

Open: JSON.parse raw duplicate-key parity, browser/Quest rendering, source honesty,
and real event provenance. No outcome/energy/causality claims are made from logs.
