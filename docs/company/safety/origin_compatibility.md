# R02 S03 - evidence origin compatibility
| Question | Acceptable initial evidence | Cannot substitute |
| --- | --- | --- |
| Python rejects invalid input | executable unit test/source review | human belief |
| Board UART voltage compatible | exact revision documentation + reviewed measurement plan | matching connector label |
| Camera pose signs correct | measured physical axis experiment | a synthetic transform test alone |
| Landing controller follows intended state transitions | offline state-machine tests | tag detector accuracy |
| Actual drone can hold position | isolated SITL then separately authorized physical validation | accepted mode service response |
| Site/operation legally permitted | owner verification with relevant authority | a generated checklist |

The software recognizes origin labels but does not authenticate them. A malicious record can lie; manual evidence review remains required.
