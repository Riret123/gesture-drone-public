# DevRel red team: Round 02

| ID | Attack | Severity | Status | Next-round acceptance |
| --- | --- | --- | --- | --- |
| D-02-01 | Root cross-review: HTTP citations and loaded img/link resources are conflated, allowing remote dependencies. | high | open | allow external anchor citations but reject remote loaded resources with tests |
| D-02-02 | Root cross-review: CSS @import and url dependencies are not parsed by the general auditor. | high | open | conservative local-CSS policy with escaped/comment cases and explicit limits |
| D-02-03 | HTML source is fully read without a byte/page resource cap. | medium | open | bounded read and page-count budget; reject oversized site input |
| D-02-04 | Unicode pipeline loss escaped initial source audit because valid ASCII question marks remain valid HTML. | high | corrected, regression pending next full suite | preserve actual Cyrillic and record write-path hazard |
| D-02-05 | Static title/main existence checks do not prove meaningful structure or accessibility. | medium | open | tighten source invariants while explicitly retaining browser/manual review blockers |
| D-02-06 | Markdown source links are manually reviewed and may drift outside the site checker. | medium | open | bounded Markdown-link audit with protected-path rejection and real repository check |

These are simulated reviews plus a real cross-worker code review. No independent browser or safety certification is claimed.
