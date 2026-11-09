# R04 E03 - bounded transient arithmetic
`evaluate_profile` now requires the keyword max_segments. This is an intentional offline API change; callers must choose an explicit resource bound. Oversized lists reject before segment inspection. The test fixture uses 16, which is not an electrical or operational limit.

Nonzero duration/current products that underflow to zero return INVALID with arithmetic_underflow rather than a falsely reassuring zero energy. Nonzero charge with zero resulting energy or RMS likewise rejects. Extreme values may conservatively reject even when a different numerical representation could compute them.

All-zero explicitly known current remains valid. Unknown values never become idle. Overflow and underflow are unavailable evidence, not failed physical components.
