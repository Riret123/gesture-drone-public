# R01 V04 - perception dataset protocol
Record only consented data needed for the experiment. Prefer tag-only imagery without people, retain no credentials or unrelated telemetry, and document retention/deletion owner. No camera collection runs here.

Each sample needs session ID, exposure configuration, marker ID/family/size, calibration ID, capture/exposure timing provenance, reference pose source and a label of whether the marker is truly visible. Include blur, partial occlusion, glare, rotation, scale, distractor tags and complete absence. Adjacent frames belong to one split to avoid leakage.

Version annotation definitions and audit disagreements rather than replacing them silently. Evaluate false acceptance on tag-absent data, false rejection on valid data, position error on accepted samples, and coverage. Report counts by stratum; no real accuracy number exists yet.
