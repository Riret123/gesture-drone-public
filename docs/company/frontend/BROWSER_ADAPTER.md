# Shared view-only browser adapter

Both dashboard and Quest now load `/telemetry_ui.js`, served from a fixed local
route by the existing loopback mock server. `/telemetry` includes schema=1.
The mock provider passes the Python normalizer's schema test.

The shared adapter checks exact fields/types/bounds, limits streamed body bytes,
uses fatal UTF-8 decoding and clears numbers on invalid or stale input. Source
age plus total request duration is compared against the existing two-second
display threshold. This conservative upper estimate does not validate acquisition
time or source honesty and introduces no flight threshold change.

History uses textContent; old history gets an explicit stale label on failure.
Reported deadman state says "NO CONTROL" when pressed, rather than implying the
view-only page enables a vehicle. Requests are sequential, GET only, with one
next poll scheduled in finally after completion. No command channel is introduced.

Run supplemental logic/fake-DOM checks: `node tools/test_telemetry_ui.cjs`.
The normal Node --test mode was blocked by sandbox child-process EPERM;
direct built-in node:test execution passes all 12 tests without child spawning.
These are not browser, accessibility or Quest rendering results.

Remaining parity limits: JavaScript JSON.parse collapses duplicate keys and
integer-token spelling; Python's decoder is stricter. The local mock server emits
known JSON, but an arbitrary future telemetry source needs a strict ingestion
boundary. Do not claim this browser parser independently rejects duplicate keys.
