# R01 S04 - assumptions requiring verification
A01: tag detector coordinates match camera optical axes. Verify with detector documentation and axis-target experiment.
A02: tag size uses the detector's specified physical boundary. Verify actual printed scale and detector convention.
A03: receive time is local monotonic and not wall/remote time. Verify adapter clock source.
A04: uncertainty is calibrated position uncertainty. Verify held-out ground truth; do not treat residual pixels as metres.
A05: robot has independent FC failsafes and pilot intervention. Verify on target under a separate procedure.
A06: disconnect removes motor power without backfeed. Verify schematic and unpowered continuity plan.
A07: use is permitted under site/aviation/student work rules. Owner must verify with appropriate authorities; no legal conclusion here.

All assumptions are unverified at run start. Evidence must identify who checked, date, revision and limitations.
