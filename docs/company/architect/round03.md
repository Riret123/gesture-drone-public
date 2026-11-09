# Architect round 03 review

Brainstorm produced five architect and five architecture-red-team ideas, scored
with explicit S/T/P/E judgments. Selected origin/revision binding plus continuous
separation; other ideas are deferred. Accepted ADR 003 and ADR 004 after code and
independent test review. Coordinate labels remain assertions, never survey proof.

Closed A-R01-1/A-R02-1 for the narrow executable metadata-refusal contract using
`require_context`; physical origin validation remains open. Closed A-R02-2 for
between-tick model crossings with analytic union-of-segments analysis. A-R02-3
remains a model limitation; A-R02-4 output byte amplification and A-R02-5 structured
diagnostics remain open for later rounds. No code connects analysis to aircraft.

New numerical policy: delayed positive segments that disappear at global float
resolution reject. Other float rounding remains visible; results are analytic to
float precision, not exact physical trajectories or certified clearance proofs.
