# R01 S01 - initial hazard register
| ID | Hazard and causal chain | Offline requirement | Evidence | Residual |
| --- | --- | --- | --- | --- |
| H01 | false tag pose drives wrong correction | exact source identity and quality rejection | observation tests | plausible false pose still possible |
| H02 | old frame appears current | separate receive age from exposure age | latency analysis | capture provenance missing |
| H03 | camera/body sign error | explicit frame contract and measured extrinsics | frame documentation | no physical calibration |
| H04 | power loss disables companion stop | independent motor isolation architecture | rover stop design | hardware unverified |
| H05 | test success misrepresented as safety | evidence labels and human release gates | acceptance records | external communication review required |
| H06 | moving pad exceeds tracking envelope | relative-motion bounds before descent proposals | planned later round | no integrated controller |

Severity is potentially severe for physical injury; occurrence probabilities are unknown. No fabricated numerical risk score is assigned.
