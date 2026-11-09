# R04 E04 - embedded prior attack fixes
E19 underflow: test_e19_nonzero_load_underflow_is_invalid_not_zero_demand proves two failure paths: duration*current loss and voltage*charge loss. Result is INVALID without misleading totals.

E21 resource bound: test_e21_explicit_segment_bound_before_iteration proves malformed oversized input is rejected by count first and boolean/nonpositive limits reject.

E05 impossible geometry: new planar checker adds concrete counterexamples for insufficient hole-edge clearance, overlapping/gapped holes, duplicate centres, impossible plate width and malformed numeric data. This closes only geometric contract checks; structural/physical evidence remains open.
