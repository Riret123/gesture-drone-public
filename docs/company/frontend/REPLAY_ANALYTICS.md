# Bounded replay analytics

Run locally from the repository root:

```text
python -B tools/analyze_replay.py tests/fixtures/replay_synthetic.jsonl --gap 2
```

This reads only the explicitly named file and prints one aggregate JSON report.
It never imports ROS or publishes commands. Empty input reports count zero with
unknown battery extrema. Invalid later input suppresses the whole report, so a
partial prefix cannot be mistaken for a complete analysis.

Fields: count, elapsed span, reported battery minimum/maximum/change, mode
transitions, count of nonempty acknowledgement rows, repeated timestamps, gap
intervals and mode dwell. A gap at the configured threshold is included. Dwell
uses the left endpoint until the next sample, with no extrapolation after the last.
No time is attributed to missing intervals beyond that explicit mathematical rule.

Do not infer a cause from a gap, energy from battery percentage, actual flight
from mode text, or completed maneuvers from an acknowledgement. A malicious source
can still lie with plausible values. Source text is bounded, controls/direction
overrides/surrogates reject, and duplicate JSON fields reject at ingestion.

Resource defaults: 10,000 events and 16,384 bytes per line. These are offline
allocation bounds, not FC or flight-safety parameters. Reads are bounded before
JSON parsing; decoding must use strict UTF-8. Human ownership and permission for
real log content remain external to this analyzer.
