# R02 E01 - executable power budget contract
`energy_budget.RailLoad` requires an exact unique load name; known voltage, continuous current, peak current and efficiency must be positive finite numbers. Unknown values are `None`, not zero. Peak demand cannot be lower than continuous demand; efficiency cannot exceed one.

`evaluate_budget` requires explicit source minimum voltage and continuous/peak current limits, already derated by the owner. All load peaks sum simultaneously. Duplicate names reject because double-counting or omitted identities may hide bookkeeping errors. Unknown load/source evidence returns UNKNOWN with no computed power/current. Overflow returns INVALID.

WITHIN_ARITHMETIC_LIMITS means only supplied current arithmetic meets supplied limits. It is not approval of wiring, fusing, battery chemistry, transient behavior or physical energizing.
