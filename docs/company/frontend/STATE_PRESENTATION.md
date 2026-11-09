# Status presentation acceptance matrix

| State | Label | Numbers | Command affordances |
| --- | --- | --- | --- |
| No sample | OFFLINE | unknown | none |
| Invalid envelope | INVALID | unknown | none |
| Age limit reached | STALE | unknown | none |
| Valid mock | MOCK DATA | visible with simulation label | none |
| Valid nonmock | RECEIVED, not verified | visible with acquisition caveat | none |

Do not encode status by color alone. Each state requires visible text and a
programmatic label. Announce state transitions rather than every telemetry poll
to avoid screen reader overload. Battery percentage has no chemistry or remaining
flight-time meaning without a validated battery model.

History may remain visible after disconnect only with a stale-history label.
Current values must clear independently of whether history is retained. A failed
poll must not leave a previous positive deadman label beside an offline banner.

Human checks: keyboard zoom at 200%, narrow viewport, large text, contrast,
screen reader state transition, Quest comfort and readability. These are pending;
static Python checks cannot demonstrate them.
