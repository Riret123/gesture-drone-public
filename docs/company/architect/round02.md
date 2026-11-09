# Architect round 02 review

Accepted ADR 001 (offline boundary), ADR 002 (analytic clocks/resources), and the
explicit origin/process trust model. See standalone documents in this folder.
These are three independently reviewable design artifacts, not a claimed count
for each heading. Backend now has a documented command that exposes only JSON
simulation output; no middleware or actuation connection exists.

Round-1 attacks: A-R01-2 fixed by summary flags and usage limits; A-R01-3 fixed
by the maximum-valid export regression; A-R01-4 fixed by total duration budget;
A-R01-5 fixed by explicit trusted-process boundary. A-R01-1 remains open for an
executable origin-binding experiment in round 03, with adapter refusal required
before navigation use. No hardware authorization is inferred from these fixes.

Next architecture priority: immutable mission digests, common ENU frame identity
for multi-agent simulation, then continuous closest-approach checking between
samples so coarse telemetry does not hide a crossing.
