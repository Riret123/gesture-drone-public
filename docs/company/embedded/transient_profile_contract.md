# R03 E01 - piecewise source-current profile
`energy_profile.CurrentSegment` specifies positive duration and nonnegative known consumption current. Explicit zero is an idle interval; unknown and negative current reject. `evaluate_profile` assumes a complete piecewise-constant waveform at a supplied constant source voltage and computes duration, peak current, time-weighted RMS current and energy.

All peaks/idle gaps must be represented. Input is not a sampled sensor stream with inferred timestamps. Explicit positive peak/RMS/energy comparison limits produce arithmetic reasons; overflow returns INVALID without numerical totals.

RMS is a mathematical summary, not a temperature model or fuse qualification. Negative regeneration is rejected because voltage rise and charge acceptance need a different model. No hardware ratings or recommended limits are supplied.
