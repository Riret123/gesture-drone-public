# Read-only interface threat model

Assets: honest status, local files, operator attention and privacy. Trust boundary:
JSON and log text enter from external sources; they are data, never instructions.

| Threat | Required defense | Evidence / remaining limit |
| --- | --- | --- |
| Bool becomes numeric battery | exact numeric type | telemetry unittest |
| Old source sample gets fresh receive time | add source age | boundary unittest; dishonest source unresolved |
| Browser script injected in ack | textContent only | existing source check; browser execution pending |
| Oversized history | envelope count/string bounds | unittest; HTTP body size still unresolved |
| Misleading healthy state | unknown clears values | normalizer tests; browser integration pending |
| Poll storm | one outstanding request and bounded retry | design requirement, integration pending |
| Hidden flight control | prohibit command transport | existing static source check, runtime review pending |

Local-only binding reduces accidental exposure but does not authenticate another
local process. No security certification is claimed.
