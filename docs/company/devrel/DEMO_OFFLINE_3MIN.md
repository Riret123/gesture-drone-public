# Three-minute offline demo script

Preparation: run the quickstart in advance from the repository root. Use a local terminal with no ROS nodes, aircraft or camera involved. Keep the safety and evidence labels visible.

0:00-0:25: Show README architecture. Say: "This is a gesture-triggered drone prototype and a set of offline control experiments. I am demonstrating software evidence, not flying an aircraft."

0:25-1:00: Run `python -B tests/run_all.py`. Explain one real failing-input test after inspecting its name in the output. Do not claim coverage percentage unless a tool has measured it.

1:00-1:30: Run `python -B tools/landing_faults.py`. Explain pose loss as a failure condition and distinguish proposal output from actual flight-controller response.

1:30-2:00: Run `python -B tools/simulate_landings.py`. State that success is defined inside the toy model; results do not predict real landing reliability.

2:00-2:35: Show one module and corresponding test. Explain input units, invalid-input behavior and remaining calibration work. Attribute AI assistance and personal contributions honestly.

2:35-3:00: End with next evidence needed: Linux/ARM environment, isolated SITL, sensor calibration and independent operational review. No physical flight is requested in this demo.

Fallback: if a command fails, show the traceback and describe the unresolved issue. Do not substitute a previous success screenshot without a clear date/environment label. Timing is a rehearsal target, unmeasured until a human walkthrough.
