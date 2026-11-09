# QA and test charter

Own reproducible adversarial checks for the offline mission/swarm contracts.
Unit tests use the standard library and execute on Windows. No test discovers
the root integration script or sends a flight command. Test count measures
executable unittest methods; subcases are recorded separately, never inflated.

Acceptance requires the full portable suite after every batch, explicit expected
results at boundaries, deterministic seeds for fuzz campaigns, and evidence for
each code attack. Documentation attacks use source/link assertions where useful;
unmeasurable claims remain blocked rather than receiving a meaningless test.

Red-team findings use Q-Rxx-n identifiers. Preserve distinctions between parser,
toy simulator, ROS mock, SITL, and physical evidence. Own no flight authorization.
