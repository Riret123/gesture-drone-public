# Offline troubleshooting

| Symptom | Likely question | Safe next step |
| --- | --- | --- |
| python not found | Is Python installed and on PATH? | record shell/version availability; arrange installation separately |
| test path missing | Are you at the repository root? | locate `tests/run_all.py`; change to its parent repository directory |
| ModuleNotFoundError in a module CLI | Was the source package path configured? | prefer the repository runner; for optional module CLIs set PYTHONPATH explicitly |
| SyntaxError | Is the interpreter compatible? | record `python --version`; do not rewrite code to hide an environment mismatch |
| PermissionError | Is this a restricted workspace? | use readable local fixtures; preserve the failure and avoid broad permission changes |
| HTTP mock port in use | Is another local process bound? | do not kill unrelated processes; inspect supported port options before restarting |
| ROS import failure | Did a hardware wrapper run? | return to portable runner; ROS target setup is a different validation lane |
| Test failure | Which test and input failed? | capture traceback, report exact command and fix the regression before continuing |

Do not run the root live integration script as a troubleshooting step. Never solve an offline test failure by connecting a physical flight controller. No automated network switching belongs in this workflow.

Acceptance: each symptom has a bounded action that does not escalate into actuation or unsupported environment edits.
