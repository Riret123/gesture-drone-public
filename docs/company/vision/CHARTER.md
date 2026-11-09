# Vision and ML charter
Owner: simulated vision engineer. Independent reviewer: simulated vision red team.

Deliver calibrated, attributable observations and measured error analysis before proposing control integration. Current work is offline pure Python; it does not detect tags, open cameras, train models or publish commands. Synthetic unit tests establish contracts, not perception accuracy.

Inputs: local monotonic receive time, exact camera/calibration identity, tag ID, camera-optical position in metres, reprojection residual in pixels, position uncertainty in metres. Outputs: accepted metadata snapshot or explicit rejection reason. Dependencies: measured marker size, physical camera model, held-out images and external frame calibration.

Acceptance: malformed input rejected, thresholds explicit, every attack linked to evidence, no accuracy claim without dataset provenance. Stop integration on unknown frame, stale observation or missing physical calibration. KPIs: tested rejection categories, held-out error quantiles once data exists, unresolved critical attacks. Do not optimize apparent acceptance rate by loosening limits.
