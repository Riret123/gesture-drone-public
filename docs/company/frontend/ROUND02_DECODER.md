# Round 02: strict ingestion

FE06 reproduced as an OverflowError using battery=10**10000. Reused the existing
strict finite predicate, which rejects bools and catches integer conversion
overflow. The regression now returns INVALID without an exception.

FE07 addressed with decode_telemetry: exact str/bytes input, explicit UTF-8,
caller-selectable bounded resource limit, duplicate object keys rejected,
nonstandard numeric constants rejected, recursion/Unicode/JSON failures mapped
to INVALID. A parser limit cannot prevent allocations already made by an HTTP
client; adapters must cap reads before constructing this input.

Eight added executable cases cover integer overflow, UTF-8 roundtrip, duplicate
keys, constants/exponents, malformed encoding, byte vs character budget, excessive
nesting/wrong top level, and configuration limits. Full shared suite: 98 passed.

No live flight safety threshold is changed. max_bytes=16384 is an offline parser
resource default; freshness limits remain explicit caller configuration.
