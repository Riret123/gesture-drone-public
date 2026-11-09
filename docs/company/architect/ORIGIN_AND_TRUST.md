# Mission origin and process trust

Version 1 has a named coordinate convention but no embedded geodetic origin.
The current evaluator assumes a single caller-established local ENU origin and
defaults its toy start to (0,0,0). Reusing a JSON route at a different location
can describe a different physical path. No current function claims to detect it.

A future adapter must bind a mission to an immutable origin identifier, mission
digest and localization-frame revision before any navigation use. A missing or
mismatched origin must refuse route execution. Merely receiving `local_enu` from
a sender does not establish that its home matches a receiver's home.

This is a design gate, not an implemented aircraft safeguard. Round 03 should
prototype a pure binding contract for simulation comparisons; real home setup,
coordinate transforms and localization remain blocked on measured target data.

Frozen values protect ordinary accidental mutation and snapshot aliasing.
They do not sandbox Python code: code with `object.__setattr__`, arbitrary imports
or process access can bypass invariants. Trust boundary is untrusted JSON bytes,
not a malicious Python plugin in the same interpreter. Use process isolation and
authentication in a separately reviewed deployment if adversarial code is in scope.

Acceptance: no docs describe a frozen dataclass as an authorization/security
boundary; no adapter emits flight commands based only on schema validity.
