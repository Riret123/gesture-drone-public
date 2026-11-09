# Frontend red team — round 2

| ID | Attack | State | Evidence / next step |
| --- | --- | --- | --- |
| FE06 | huge integer overflows isfinite | fixed | reproduced failure then passing huge-integer regression |
| FE07 | duplicate JSON fields bypass schema | fixed | duplicate-key decoder regression |
| FE10 | multibyte text slips under character budget | fixed | character_and_byte_budgets test |
| FE11 | NaN/Infinity or giant exponent becomes healthy | fixed | nonstandard_constants_and_huge_exponent test |
| FE12 | invalid UTF-8/surrogates crash ingestion | fixed | malformed_utf8_surrogate_and_bom test |
| FE13 | deep nesting causes recursion exception | fixed | depth_and_wrong_top_level test |
| FE14 | malformed payload with invalid max_age returns INVALID instead of rejecting configuration | open | make config validation consistent in round 3 |
| FE15 | HTML text passes Python contract | open by design | consumer must escape; browser parity tests needed |
| FE05 | forged local timestamp | open | adapter ownership and session model |
| FE08 | browser schema weaker than helper | open | browser adapter not yet integrated |
| FE09 | replay with refreshed source age | open | sequence/session gate experiment |

The decoder rejects input after its caller has allocated it. HTTP body allocation
and decompression bombs remain outside this helper's boundary.
