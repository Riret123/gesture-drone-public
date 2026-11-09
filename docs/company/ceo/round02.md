# Round 02 product decisions and retrospective

Goal: fix evidence/accounting gaps from Round 01 and establish safe contracts for deeper work.

Decision C02-01: deliverable accounting now distinguishes modules, collected tests, designs, analyses and review findings. See DELIVERABLE_ACCOUNTING.md. Do not sum duplicate categories to manufacture 500 outputs.

Decision C02-02: blocked work continues through local substitutes under REVIEW_GATES.md. Actual board/SITL/market permission remains blocked.

Decision C02-03: five-minute review is a usability target with an observation protocol, not a measured promise.

Decision C02-04: architecture source of truth currently defines mission v1 as local ENU with explicit future home, bounded JSON and no live importer. See ../architect/round01.md and ../architect/round02.md. Presentation must preserve this distinction. New telemetry contracts are separately owned by Frontend and must not be implied to supply flight guards.

Decision C02-05: business priorities are preparation value, not income forecasts. Physical product commercialization is deferred; offline lessons and read-only reports are better local experiments while eligibility and demand remain unverified.

Decision C02-06: DevRel owns static docs/site and a source audit that never fetches URLs or reads protected trees. Site source checks do not prove browser rendering, usability or translation quality.

Decision C02-07: the full suite is a changing shared snapshot. A reported count must include when it ran and cannot be treated as the final repository total while workers edit.

Decision C02-08: Round 03 brainstorm should favor evidence traceability, failure explanations and bounded tools. Reject ideas that need live routing changes or pretend mock telemetry is a live safety layer.

Retrospective: broad artifact creation is fast; trustworthy evidence takes careful boundaries. The valuable corrections were distinguishing preparation from revenue, design from validation and test counts from deliverable quality. Continue deeper executable audits rather than expanding claims.
