# R02 E04 - rail topology review
Separate source, regulator, consumer and protection nodes. Label each connection with current direction, voltage envelope and reverse-current behavior. Account for efficiencies at each conversion stage exactly once; current implementation models each load's total path efficiency from source to load, not a reusable shared-regulator graph.

Shared regulator losses cannot be independently summed from incompatible per-load efficiency guesses. If a shared converter is chosen, derive a total-load efficiency model from its data and apply it at the combined operating point. Identify backfeed through USB, UART protection and sensor power.

Current blocker: no chosen topology or schematics. Do not populate it with assumed board pinouts. Motor and companion power failure domains need separate review.
