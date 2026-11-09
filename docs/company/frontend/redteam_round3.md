# Frontend red team — round 3 pre-brainstorm review

| ID | Attack | State | Evidence / next action |
| --- | --- | --- | --- |
| FE14 | config errors depend on payload validity | fixed | decoder_invalid_config_always_raises |
| FE05 | timestamp supplied by remote source | mitigated offline | TelemetrySession owns receive call time; caller still trusted |
| FE09 | replay same sequence refreshes view | fixed within session model | duplicate_sequence_invalidates_instead_of_renewing |
| FE16 | mutation after receive rewrites current view | fixed | payload_mutation_cannot_rewrite_snapshot |
| FE17 | slow response with age=0 appears fresh | fixed display logic | Node slow-success test |
| FE18 | boolean battery becomes 1 percent in browser | fixed display logic | Node numeric-impostor test |
| FE19 | injected ack becomes markup | fixed fake-DOM boundary | Node textContent test; actual browser pending |
| FE20 | body too large before JSON parse | mitigated | streaming byte cap; response headers/server allocations out of scope |
| FE21 | same schema means identical Python/JS raw parser | open | JSON.parse duplicate-key/integer-token differences disclosed |
| FE22 | UI values stay healthy while next fetch hangs | open | polling clears after timeout, watchdog display deadline needed |
| FE23 | system sleep freezes JavaScript updates | open | no display can update while runtime suspended; resume invalidation needed |
| FE24 | external script breaks direct file opening | open | serve through mock server; offline site must remain independent |

Previous FE08 weak browser schema now mitigated by shared normalizer and mock
provider conformance; FE21 remains explicit raw-decoder discrepancy. FE15 escaping
now has a fake-DOM regression; physical browser behavior remains unverified.
