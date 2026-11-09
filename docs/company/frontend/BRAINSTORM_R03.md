# Round 03 brainstorm — frontend and its red team

These are proposals from two simulated roles, not a survey of independent people.
Scores are subjective planning judgments: uncertainty reduced (U), reproducibility
(R), effort feasibility (F), each 1–3; total U+R+F. No commercial value is inferred.

| ID | Proposer | New idea | U/R/F | Vote rationale |
| --- | --- | --- | --- | --- |
| F03-1 | Frontend | bounded log timeline analytics with no actuation | 3/3/3 | inspect failures without hardware |
| F03-2 | Frontend | announce only changed status for screen readers | 2/2/3 | reduce repeated poll noise |
| F03-3 | Frontend | shared JSON contract fixture comparison across Python and JS | 3/3/2 | reveal parser/type drift |
| F03-4 | Frontend | clickable evidence labels for each site feature | 2/3/2 | align claims with tests |
| F03-5 | Frontend | keyboard-only camera workflow rehearsal | 2/2/2 | source checks plus human protocol |
| FR03-1 | Frontend red team | adversarial log corpus with duplicate keys and clock reversal | 3/3/3 | falsify analytics assumptions |
| FR03-2 | Frontend red team | replay of reordered UI timeout callbacks | 3/3/2 | expose stale callback races |
| FR03-3 | Frontend red team | Unicode/bidi spoof corpus for labels | 3/3/2 | misleading text beyond HTML injection |
| FR03-4 | Frontend red team | ack correlation ambiguity demonstrator | 3/3/2 | acceptance cannot establish outcome |
| FR03-5 | Frontend red team | local asset route matrix and traversal tests | 2/3/3 | prevent filesystem pass-through regression |

Vote: both roles choose F03-1 with FR03-1 as its adversarial acceptance work.
Tie broken by immediate relevance to existing recorder and must-cover analytics.
Implement bounded read-only analysis and hostile-input tests in this round.
F03-3 is next; DevRel owns F03-4 integration. No votes authorize live changes.

Prior expiry and visibility fixes were already implemented before this brainstorm;
they are not represented as newly voted ideas or counted again.
