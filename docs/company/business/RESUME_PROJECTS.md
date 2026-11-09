# Projects to put next on my resume

Twelve future project ideas ranked by subjective aerospace engineering skill visibility and feasibility, not an admissions or hiring probability. All are proposals until individually implemented and reviewed. Personal contribution must be recorded. The two-week plans assume available study time; actual effort and costs: verify. No aircraft actuation or paid work is authorized.

## 1. Reproducible flight-policy fault laboratory

Scope: exercise pure state machines with delayed, missing and malformed telemetry. Stack: Python standard library, unittest, JSON fixtures, optional later ROS 2 mocks. Deliverables: fault catalog, deterministic runner, state trace, tests and limitations report.

Week 1: days 1-2 specify inputs/units and invalid-data behavior; 3-4 implement bounded fixtures; 5-7 write delayed/lost/reordered cases. Week 2: days 8-10 reproduce each failure and fix; 11-12 compare expected traces; 13-14 write a source-linked case study and demo.

Resume evidence: a reviewer can rerun a named failure and inspect the guard. Claim only tested synthetic behavior, not aircraft safety.

## 2. Moving landing-platform simulation and uncertainty study

Scope: analyze relative pose, stale observations and moving-target assumptions without motors. Stack: Python, deterministic kinematics, JSON/CSV, optional plots generated separately. Deliverables: model equations, scenarios, failure boundaries, replay traces and sensitivity discussion.

Week 1: days 1-2 define frames and assumptions; 3-4 implement relative motion; 5-7 add latency and pose loss. Week 2: days 8-10 sweep seeded cases; 11-12 identify model omissions; 13-14 present results with uncertainty and next calibration experiment.

Resume evidence: reproducible model and falsifiable limitations. Do not call simulated completion real precision landing.

## 3. Mission JSON validator and read-only simulator

Scope: validate waypoint schemas and compute a bounded offline path trace. Stack: Python, JSON, unittest, static report. Deliverables: versioned schema, bounds checking, duration/path estimates, rejection examples and tests.

Week 1: days 1-2 specify units/frame and bounds; 3-4 parser and duplicate/unknown-field checks; 5-7 waypoint ordering and path calculation. Week 2: days 8-10 malformed/fuzz cases; 11-12 review nonphysical assumptions; 13-14 demo accepted and rejected missions.

Resume evidence: interface design and defensive input handling. Estimates do not imply endurance, obstacle clearance or executable autopilot missions.

## 4. Sensor frame calibration notebook and contract

Scope: document camera/body/world coordinate conventions and test known transforms. Stack: Python, linear algebra helpers, synthetic fiducials, optional later OpenCV. Deliverables: frame diagrams, test vectors, calibration procedure, residual definition and evidence template.

Week 1: days 1-2 choose conventions; 3-4 derive transform composition; 5-7 test rotations, handedness and units. Week 2: days 8-10 add wrong-frame attacks; 11-12 create calibration record template; 13-14 demonstrate why a sign error changes a landing proposal.

Resume evidence: aerospace frame reasoning and reproducible test vectors. No measured calibration accuracy without actual observations.

## 5. Battery telemetry uncertainty and reserve model

Scope: compare advisory state-of-charge inputs, hysteresis and missing-data behavior offline. Stack: Python, CSV fixtures, unittest. Deliverables: chemistry assumption sheet, load-sag scenarios, reserve-policy trace, tests and review checklist.

Week 1: days 1-2 define valid telemetry and chemistry unknowns; 3-4 implement advisory model; 5-7 add load/measurement scenarios. Week 2: days 8-10 test hysteresis and stale data; 11-12 analyze false confidence; 13-14 report limits and required bench measurements.

Resume evidence: systems reasoning under uncertain telemetry. Do not advertise endurance or set FC battery failsafes from the toy model.

## 6. Read-only flight-log replay and anomaly report

Scope: validate local event logs and summarize gaps, invalid fields and state transitions. Stack: Python csv/json/statistics, unittest, static HTML. Deliverables: versioned log contract, bounded loader, replay viewer, anomaly report and provenance record.

Week 1: days 1-2 define allowed fields and privacy limits; 3-4 parse fixtures; 5-7 compute timing/gap summaries. Week 2: days 8-10 adversarial records and encoding tests; 11-12 build report; 13-14 explain one anomaly without claiming a cause beyond evidence.

Resume evidence: data engineering plus safety-aware interpretation. Replay never republishes commands and analysis is not a flight clearance.

## 7. Gesture ambiguity and temporal robustness evaluation

Scope: quantify a classifier on consented or synthetic landmark sequences with explicit unknown handling. Stack: Python, JSONL/CSV, unittest; optional separate MediaPipe collection. Deliverables: dataset card, split policy, confusion matrix tool, temporal scenarios and limitations.

Week 1: days 1-2 define labels/privacy; 3-4 build synthetic sequences; 5-7 evaluate ambiguity and loss. Week 2: days 8-10 test debounce effects; 11-12 inspect errors; 13-14 report dataset limitations and future consented collection protocol.

Resume evidence: evaluation discipline rather than a claimed real-world recognition percentage. Synthetic landmarks do not establish camera accuracy.

## 8. Multi-agent separation and scheduling simulator

Scope: simulate a few named vehicles sharing a landing resource with bounded local positions. Stack: Python, unittest, seeded scenarios, JSON traces. Deliverables: identity contract, separation checks, reservation state machine, starvation scenarios and trace viewer.

Week 1: days 1-2 define identities and no-communication assumptions; 3-4 implement reservation; 5-7 add simultaneous requests. Week 2: days 8-10 stale/duplicate identity attacks; 11-12 analyze fairness/deadlock; 13-14 present model boundaries.

Resume evidence: distributed systems reasoning. This is not a demonstrated swarm controller or collision-avoidance guarantee.

## 9. Rover power and mechanical integration dossier

Scope: document a disabled rover/landing-pad concept with load, wiring and fit assumptions. Stack: OpenSCAD, Python calculators, dimension tables. Deliverables: parametric concept parts, power-budget template, interface wiring table, hazard review and bench inspection plan.

Week 1: days 1-2 inventory unknown ratings; 3-4 CAD interfaces; 5-7 power/load calculations with symbolic or verified inputs. Week 2: days 8-10 fit/clearance attacks; 11-12 review failure modes; 13-14 prepare non-powered inspection record.

Resume evidence: multidisciplinary hardware documentation. No motor driver enablement, verified structural rating or fabrication suitability is implied.

## 10. Quest view-only telemetry usability study

Scope: display mock state, age and uncertainty in an accessible read-only HUD. Stack: static HTML/CSS/JavaScript, JSON fixtures, browser tests when available. Deliverables: schema, mock HUD, loss/stale states, keyboard/accessibility review and usability protocol.

Week 1: days 1-2 define labels and data age; 3-4 implement display; 5-7 add invalid/mock/stale fixtures. Week 2: days 8-10 inspect contrast and no-command transport; 11-12 rehearse a human study; 13-14 report actual rendering tests separately from source checks.

Resume evidence: human factors and interface clarity. Quest rendering and operator performance remain unverified until observed.

## 11. Bilingual voice intent and negative-command corpus

Scope: parse exact RU/EN text intents while rejecting ambiguity and negation; no microphone or command publisher. Stack: Python Unicode handling, unittest, JSON corpus. Deliverables: phrase specification, negative examples, parser tests, normalization policy and safety review.

Week 1: days 1-2 specify accepted phrases; 3-4 implement exact matching; 5-7 add negation, mixed-language and punctuation cases. Week 2: days 8-10 adversarial Unicode/partial-match tests; 11-12 fluent review; 13-14 demo rejection behavior and audio-recognition gap.

Resume evidence: careful interface design. Text parsing does not establish speech recognition accuracy or authority to actuate.

## 12. Offline engineering documentation site and evidence index

Scope: package safe tutorials, architecture, limitations and reproducible evidence for offline review. Stack: static HTML/CSS, Python link checker, unittest. Deliverables: navigation, evidence labels, EN/RU glossary, command audit and accessibility checklist.

Week 1: days 1-2 inventory sources; 3-4 build navigation; 5-7 write safe tutorials. Week 2: days 8-10 link/encoding checks; 11-12 novice walkthrough; 13-14 revise portfolio narrative and attribution.

Resume evidence: technical communication and reproducibility. A polished site cannot replace measured engineering results.

## Choosing one

Pick one top-ranked project that Emir can explain and complete with existing equipment and coursework. Verify advisor relevance and any school/IP restrictions. Prefer depth in a single case study over listing twelve unfinished projects. Costs and available time must be checked by the human before starting.
