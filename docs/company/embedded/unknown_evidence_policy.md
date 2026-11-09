# R02 E05 - unknown is not zero
Missing voltage, current, efficiency or source capacity returns UNKNOWN and suppresses totals, even when other loads are known. Partial totals can look reassuring while omitting the dominant load, so this API does not produce a passing partial budget.

Data owner must distinguish manufacturer nominal, manufacturer limit, measurement and estimate. Use the conservative documented value appropriate to each case; do not silently round away peaks. A missing peak is not continuous current; a missing regulator efficiency is not one.

R01 E03 simultaneous-peak and E06 unknown-evidence attacks now have executable regressions in tests/test_energy_budget.py. Real values and physical protection remain unverified.
