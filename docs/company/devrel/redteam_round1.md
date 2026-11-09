# DevRel red team: Round 01

| ID | Attack | Severity | Status | Required next-round evidence |
| --- | --- | --- | --- | --- |
| D-01-01 | Quickstart may drift when module CLIs change. | medium | open | execute every documented portable command and record output/exit status |
| D-01-02 | Glossary translation has no fluent technical reviewer. | medium | open | mark translation draft and add a meaning-preservation review checklist |
| D-01-03 | A timed demo could hide failures by using rehearsed output. | high | open | add recording provenance and visible failure policy to demo evidence |
| D-01-04 | Source policy asks for direct module references but the navigation draft is mostly names. | medium | open | add verified relative file links and link checks |
| D-01-05 | Contribution template could become a claim of work already done. | high | open | add an example explicitly labeled fictional and separate actual attribution ledger |

These attacks concern documentation and evidence. Portable tests cannot establish translation quality or actual reviewer comprehension.

## Round 02 dispositions

D-01-01 fixed by executed-command snapshot; D-01-02 fixed-as-documentation by draft label and review protocol, fluent review remains blocked; D-01-03 fixed-as-documentation by provenance policy; D-01-04 fixed by source links/static-site audit; D-01-05 fixed-as-documentation by separate actual attribution ledger and explicitly fictional example. No human comprehension or translation claim is closed by tests.
