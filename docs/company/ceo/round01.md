# Round 01: establish evidence before expansion

Status: local planning artifacts reviewed from a product perspective; hardware and customer hypotheses unverified.

## C01.1 Product vision

Build a reproducible robotics portfolio that lets an aerospace reviewer inspect a safety decision, replay a failure, and distinguish simulation from aircraft capability in five minutes. The core user is Emir preparing for research, internship or admissions conversations. Teachers and hobbyists are secondary hypotheses, not established customers.

Acceptance: every highlighted feature has a runnable offline example or is explicitly labeled design. Avoid promoting an integrated autonomous aircraft; the repository currently implements gesture-triggered requests and disconnected policy experiments.

## C01.2 First-round priorities

1. Preserve the live control boundary: no automatic adoption of experimental policies.
2. Establish ownership and concrete deliverable accounting.
3. Inventory missing evidence for portable logic, target deployment and business claims.
4. Give reviewers a repeatable offline entry point.
5. Put all income paths behind individual eligibility verification.

Acceptance: a change that improves a count but obscures one of these priorities is rejected.

## C01.3 Evidence ladder

| Level | Evidence | Permitted wording | Does not establish |
| --- | --- | --- | --- |
| E0 | Written proposal | designed / proposed | executable behavior |
| E1 | Pure-Python test | exercised synthetic inputs | sensor accuracy or dynamics |
| E2 | Toy simulation | simulated in stated model | aircraft stability or real success rate |
| E3 | Isolated SITL record | observed in recorded SITL setup | hardware timing or airworthiness |
| E4 | Authorized controlled hardware record | observed under documented conditions | broad reliability or certification |

Historical notes do not promote a new artifact to E3. Tests from this run are E1 unless a stronger recorded environment exists.

## C01.4 KPI definitions

Track distinct accepted artifact IDs, collected unittest cases, failing test cases, open attack IDs by severity, resolved attack IDs with evidence, blocked external validations, and reproducible tutorial entry points. Record elapsed wall time separately from progress.

Do not use files, lines, repeated tests, brainstorm votes or copied checklists as independent quality indicators. A deliverable can be a substantive section, but its ID must have a distinct purpose and acceptance condition. The 500+ target is an output ambition, not permission to invent results.

## C01.5 Twelve-round product sequence

| Round | Product question | Required evidence |
| --- | --- | --- |
| 01 | What can we honestly claim now? | evidence and ownership baselines |
| 02 | What invalid input escapes the interfaces? | first attack fixes and regression cases |
| 03 | Which ideas reduce uncertainty most? | scored brainstorm with adopted ideas |
| 04 | Can a novice reproduce the offline path? | tutorial walk-through and failure handling |
| 05 | Can landing proposals explain failure? | replay and fault trace |
| 06 | Can interfaces survive loss and ambiguity? | second brainstorm and stale-data tests |
| 07 | Are growth options compatible with constraints? | eligibility and demand gates |
| 08 | Can hardware designs be inspected safely? | power/fit assumptions and disabled outputs |
| 09 | What should be cut? | third brainstorm and scope reduction |
| 10 | Is portfolio evidence attributable? | contribution and source ledger |
| 11 | Can handoff be reproduced? | command audit and blockers |
| 12 | What remains unsafe or unverified? | final red-team closure and next steps |

This is a plan; no row is marked complete by creating this table.

## C01.6 Scope and refusal boundaries

Allowed: standard-library logic, synthetic fixtures, view-only pages, local documentation, designs, mocks and toy simulations. Live ROS wrapper changes need explicit contract review and isolated SITL validation before use; this run prioritizes keeping experiments disconnected.

Not authorized: real-motor arming, physical flight, automatic network switching, secrets, git commands, account creation, customer messaging, purchases or income activity. A legal checklist does not certify eligibility. No company simulation role may override these boundaries.

## C01.7 Dependency/blocker map

Target Linux/ARM access blocks ROS imports, colcon install, camera/MediaPipe compatibility and actual board performance. Physical hardware evidence blocks fit, power, wiring and sensor calibration. Independent operational authorization blocks flight testing. School/legal confirmation blocks income experiments. Customer interviews block demand conclusions.

Continue useful offline work against documented interfaces while a blocker is open. Never fabricate a response, measured price, success rate or permission to close it.

## C01.8 Round acceptance and next work

Accept the three role charters, evidence ladder and safe offline onboarding drafts as local artifacts. Market notes must remain hypotheses; the monetization shortlist may rank preparation value but cannot forecast income. Round 02 must answer the five CEO red-team attacks, reconcile counts with actual artifacts, and turn source assumptions into a claim ledger.

Retrospective: the prior 42-item run already supplied broad scaffolding. This run should deepen malformed-input handling, failure narratives, reproducibility and evidence traceability instead of renaming old modules as new deliverables.
