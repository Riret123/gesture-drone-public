# Safe offline quickstart

Audience: a reviewer with Python on Windows or Linux. Run from the repository root; Python 3.12 is the currently documented local version. No ROS, camera, aircraft or third-party package is required for the portable suite.

1. Run `python --version` and record the result.
2. Run `python -B tests/run_all.py`.
3. Require a final `OK` and process exit code 0. A test count is not fixed here because later batches add cases.
4. Run `python -B tools/landing_faults.py`; inspect the named boolean outcomes and require exit 0.
5. Run `python -B tools/simulate_landings.py`; read results as toy-model output only.

The runner adds the source package paths itself. It excludes the root live bridge integration script and ROS package lint tests. Do not replace it with broad root discovery: the repository also contains hardware-dependent scripts.

If Python is unavailable, stop and arrange a standard Python installation through your normal environment process. If tests fail, save the failing test name and traceback, do not suppress failures or start ROS to make the portable run pass. No command above arms, publishes flight commands or opens a camera by design.

Acceptance: all three commands complete offline; failure names remain visible. Evidence limit: Windows logic checks cannot establish Linux/ARM import compatibility, actual recognition accuracy, flight dynamics or motor safety.
