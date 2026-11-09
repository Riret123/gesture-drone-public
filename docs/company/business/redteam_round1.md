# Business red team: Round 01

Simulated adversarial review. Every demand, price, income, individual eligibility and hiring/admissions outcome assumption remains UNVERIFIED.

| ID | Attack | Severity | Status | Next-round closure condition |
| --- | --- | --- | --- | --- |
| B-01-01 | The scan names broad segments without direct customer evidence; a segment is not demand. | high | open | add evidence thresholds and explicit rejection criteria for each segment |
| B-01-02 | Ten plans share unknown first-dollar timing and costs, so ranking could appear more certain than it is. | high | open | separate preparation rank from revenue rank; provide a symbolic cost model and sensitivity questions |
| B-01-03 | The 90-day plan could be mistaken for permission to conduct unpaid research or services. | high | open | make eligibility gate explicit at each external-facing milestone; maintain local-only alternative |
| B-01-04 | Competition links do not establish individual or university eligibility, deadlines or awards. | medium | open | produce program verification worksheet with unknown fields and official source dates |
| B-01-05 | Resume project ordering might imply admissions effectiveness without evidence. | high | open | define ranking rubric as subjective skill visibility, add contribution/evidence acceptance per project |
| B-01-06 | Market links show existing ecosystems, not competitor pricing or feature parity. | medium | open | compare alternative workflows qualitatively and leave price/feature claims verify until sourced |
| B-01-07 | Translation and documentation services require reviewed competence; bilingual text alone is insufficient. | medium | open | add review and rejection requirements before any service hypothesis advances |
| B-01-08 | Hardware kits and CAD can be used in flight-critical ways despite disclaimers. | high | open | document forbidden claims, design review needs and reasons to defer physical products |

No attack is closed by adding an optimistic revenue estimate. External verification blockers remain blocked rather than being silently resolved with prose.

## Round 02 dispositions

All eight documentation gaps have responses in round02.md and its named artifacts. Status: FIXED-AS-DOCUMENTATION for B-01-01 through B-01-08. External demand, individual authorization, costs, program eligibility and competence remain UNVERIFIED/BLOCKED; no claim of real-world validation is made. B-01-03 is addressed by the explicit external-action gate appended to ACTION_PLAN_90_DAYS.md.
