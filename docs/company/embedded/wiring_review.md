# R01 E03 - unpowered wiring review
Create a net table before any physical connection: source connector and pin, destination connector and pin, direction, nominal/range voltage, current, ground/reference path, protection, evidence source and reviewer. Blank fields block approval.

Check signal logic levels both directions, independent power domains, back-power through USB/UART, shared-ground fault paths, swapped TX/RX, polarity, strain relief and connector retention. Do not assume a UART label identifies voltage tolerance. Do not power the FC from competing sources without documented power-path behavior.

Physical inspection here requires propellers removed and motor power disconnected. It does not permit energizing, arming or testing motors. Owner must obtain board-specific documentation before populating pin numbers.
