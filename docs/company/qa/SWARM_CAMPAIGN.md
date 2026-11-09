# Continuous separation acceptance campaign

Independent geometry oracles cover perpendicular paths crossing between coarse
ticks, head-on meeting, constant-distance parallel paths, and vertical offset.
Occupancy tests include delayed launch, stationary zero-duration plans and final
endpoint occupancy after completion. A finite horizon clips a later collision.

Metamorphic oracles: swapping pair inputs preserves metrics; translating both
paths by the same valid ENU vector preserves metrics. Dense oracle uses seed 7742,
20 random two-agent scenarios, 1,001 time observations each over ten seconds.
Analytic minimum must be <= smallest observed distance plus 1e-10 metres, and
distance at the reported time must agree to ten decimal places. Dense checking
does not prove global correctness but independently challenges ordinary cases.

Interface attacks test duplicate IDs, malformed fleets, missing origin binding,
different origin/revision, invalid clocks/thresholds, mutable start aliasing and
positive intervals erased by a delayed global clock. Threshold equality conflict
is tested exactly for the constant-distance parallel case. No production epsilon
or minimum separation parameter was silently changed to make tests pass.

Precision regression: perpendicular/vertical crossing time differs from the
exact expected time by about one floating-point ulp. Tests use 12-decimal
almost-equality for analytic oracle comparisons. This does not establish a bound
for arbitrary near-threshold cases; that limitation remains an open attack.

Run `python -B tests/run_all.py` for the full portable suite. Focused mission and
swarm files contain their own source-path bootstrap and use only unittest.
No test starts ROS, opens serial ports, publishes commands or arms any motor.
