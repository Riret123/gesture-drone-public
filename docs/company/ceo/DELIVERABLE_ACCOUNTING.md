# Deliverable accounting and evidence rules

Round 02 response to C-01-01. Count distinct useful outputs, not every heading. A substantial analysis can be a deliverable if it answers a different question, has explicit acceptance and can be reviewed independently. A heading that restates another artifact is not another output.

Count examples: one bounded parser module; one independent regression test method; one documented interface decision; one actionable cost model; one complete tutorial. Do not count each assertion, data row, generated copy, passing rerun, file rename, boilerplate section, vote or attack status edit.

Review findings are tracked separately from implementation deliverables. An attack can motivate a test and a fix, but the finding itself does not automatically create three accepted product outputs. A charter is governance, not flight capability.

Per-artifact record: ID, role, round, path, type, purpose, status, evidence command or manual criterion, evidence level, unresolved risk and superseded-by. Allowed statuses: proposed, reviewed, fixed-as-documentation, implemented-offline, tested-synthetic, blocked, rejected. Never label external validation complete because local prose describes it.

A test method with several subcases counts as one test case in the final collected unittest total. Subcases can be discussed but not inflated into separate collected tests. New tests and all collected tests must be distinguished from the 60-case baseline.

Final reporting must show totals by category and avoid adding overlapping categories into a misleading grand total. An artifact catalog can support auditing but cannot prove substantive quality. Product review remains necessary.
