# Bounded separation benchmark

Observed 2026-11-09 during round 03 on this Windows Python 3.12.13 environment:

| Parameter | Value |
| --- | --- |
| Agents | 32 |
| Points per mission | 256 |
| Segments per agent | 511 |
| Pair comparisons | 496 |
| Horizon | 600 simulated seconds |
| Agent delay offsets | i × 0.003 seconds |
| Elapsed analysis wall time | 9.681569900014438 seconds |

Reproduction recipe: points `Waypoint('p'+str(i), i%2, (i%3)*.1, 1, .1)` for
i=0..255; Mission speed=1; common caller origin `benchmark`, revision=1; agent
start=(0,0,1), delay=i*.003 for i=0..31; `assess_fleet(agents,600,.5)` measured
once with `time.perf_counter`. Imports and plan construction excluded from timing.
The first point equals start, hence 511 rather than 512 positive segments.

This is one local measurement, not a distribution, throughput guarantee or
Orange Pi estimate. The plan deliberately shares paths and triggers conflicts;
it tests workload shape, not successful coordination. CPU identity/load and
power/thermal behavior were not measured. Do not use this timing as a control
loop deadline or network/FC latency claim.

Review led to binary search for trajectory segment lookup. A separate regression
compares it against a linear reference at all starts and midpoints for a 256-point
mission. No timing assertion is put in unittest because CI hardware varies.
