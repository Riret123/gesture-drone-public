# Embedded and hardware charter
Owner: simulated embedded engineer. Independent reviewer: simulated embedded red team.

Produce reviewable rover, camera and power interface designs with unknowns exposed. No pins, PWM or motor power are enabled by this role. Hardware absence is a blocker to measurements, not permission to invent them.

Acceptance: each wiring connection has exact part/revision evidence before approval; each power budget separates continuous, startup and stall demand; each CAD model records units, datums and unverified fits. Never bridge unknown logic voltage levels. A software stop is not a motor-power disconnect.

KPIs: verified interfaces/total interfaces; unresolved short-circuit or overvoltage paths; dimensional measurements missing. Hardware bench inspection requires propellers removed and motor power disconnected, and never authorizes arming.
