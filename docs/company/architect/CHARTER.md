# Systems Architect charter

Own versioned offline interfaces, trust boundaries, frame/time conventions,
failure semantics, and architecture decisions. Authority stops at proposals;
the live ROS bridge and flight controller remain outside this workstream.

Accept an interface only when invalid input is rejected, units are explicit,
bounded resources are specified, and a portable regression demonstrates the
contract. Red-team findings use stable A-Rxx-n identifiers and remain open until
evidence is linked. Hardware and ROS claims require target evidence, not unit tests.

Round outputs: interface decision, data contract, dependency map, fault boundary,
resource budget, migration rule, acceptance gate, and a risk review. A document
section counts only when it makes a separately reviewable decision.
