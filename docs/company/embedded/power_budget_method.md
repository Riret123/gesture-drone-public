# R01 E02 - power budget method
No electrical ratings are asserted. For each rail collect voltage range, continuous current, startup peak, peak duration, source/regulator current limit, regulator efficiency versus load, ambient/thermal limit, conductor resistance and connector rating. Use measured or manufacturer values with provenance and uncertainty.

Compute load power as voltage times current per operating case; derive upstream current from efficiency at that case, not nominal marketing efficiency. Simultaneous motor stalls and servo startup must be separate worst-case rows. Companion brownout may remove the software watchdog; motor isolation must not depend solely on companion execution.

Keep propulsion power disconnected in this run. Bench power inspection is unpowered. Battery chemistry, cell count, fuse selection and charger compatibility remain verify tasks, not purchasing recommendations.
