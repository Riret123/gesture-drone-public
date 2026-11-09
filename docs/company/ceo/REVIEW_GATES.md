# Review gates and blocked-work rules

Round 02 responses to C-01-02 and C-01-04. Continue useful offline work while preserving unresolved external gates.

Gate G1, contract: name inputs, units, frames, clock origin, bounds, unknown-data behavior and outputs. Dependents cite the actual interface. If a contract changes, update consumers and rerun the suite; do not pretend all workers approved an undocumented assumption.

Gate G2, implementation: keep pure logic separate from ROS/hardware wrappers; no import-time actuation or hidden network access. A design-only artifact must say so.

Gate G3, adversarial review: at least five concrete attacks per role per round. Each attack has an ID, expected failure, severity and next-round disposition. Same-author red-team perspectives are simulated reviews, not independent certification.

Gate G4, regression: run the complete portable suite after every batch, fix failures before accepting the batch, and preserve environment/command/count. Tests cannot close customer, legal, translation or hardware claims.

Gate G5, evidence promotion: E0 design to E1 synthetic tests needs actual results; E2 toy model to E3 SITL requires recorded isolated target evidence; E4 hardware requires separate human authorization. Blocked gates stay blocked.

Replan rule: if a dependency is unavailable, identify a local-only substitute such as schema validation, synthetic fault input, design review or documentation. Do not implement a live adapter simply to remove a blocker. Reject work that needs safety exceptions, credentials, git commands, network-folder edits or unsupported external action.

Round completion means its local outputs have review and regression evidence, not that every external gate is closed. Final handoff must preserve the blocked list.
