# R02 S02 - evidence review workflow
Choose the exact experiment and revision. Define required keys and allowed origins before collecting results. A reviewer checks each referenced artifact, who produced it, instrument/model, applicability, date and limitations. Only then may metadata completeness inform the next offline task.

Record failures as failed records rather than deleting them; record missing results as missing. Resolve duplicates explicitly rather than letting the last record win. Revisions change when relevant hardware, calibration, model, configuration or procedure changes; old records must not migrate automatically.

The current schema uses local monotonic age within one session. Long-lived calendar evidence requires a separate persistent time/provenance model, not conversion of wall time into these floats.
