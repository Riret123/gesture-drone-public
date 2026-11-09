# R01 V02 - quality limit experiment
`ObservationLimits` requires five explicit positive finite limits; there are no operational defaults. The depth interval must increase. Age, reprojection error and uncertainty limits are inclusive at the boundary; beyond them observations reject. Positive depth is mandatory through the configured minimum.

Tests use 0.2 s age, 2 px reprojection, 0.04 m sigma and 0.1-3 m depth as synthetic fixtures only. These are proposed experiment values, not flight limits and not a modification of existing landing/gesture behavior.

Before deriving limits: collect stationary and moving-target images, synchronized ground truth, camera exposure settings, marker dimensions and distance/angle strata. Split by recording session and physical marker, not adjacent frames. Report translation error quantiles and invalid-detection rate separately from rejection rate. Reprojection error is not a guaranteed bound on position error; uncertainty is a supplied estimate requiring empirical calibration.
