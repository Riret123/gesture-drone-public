# Freshness is interface-specific

| Interface | Time origin | Equality at max age | Additional checks |
| --- | --- | --- | --- |
| telemetry normalizer/session | local receive plus source-declared age | stale | receive monotonic, session sequence |
| browser display | source-declared age plus whole request duration | stale | body/type limits, display expiry |
| tag ObservationGate | local receive metadata | accepted | identity, quality, depth |
| tag capture experiment | declared shared capture clock | see capture decision table | capture sequence and origin |

These policies have different purposes and cannot be composed by assuming the
word "fresh" means the same thing. The tag inclusive boundary is an explicit
offline contract, not evidence that a real detector meets its bound. Floating
point boundary fixtures must use exactly representable values when equality is
the intended condition. No numerical epsilon is silently added to admit old data.

Browser expiry is an additional view-only timer. It clears values even if a new
request is pending; revision checks prevent an older expiry clearing a newer
accepted sample. Visibility changes invalidate in-flight results and old values.
A suspended runtime cannot update its screen, so human users must never infer
vehicle state from a frozen HUD. Resume handling reduces stale reuse after the
runtime resumes, not during suspension.
