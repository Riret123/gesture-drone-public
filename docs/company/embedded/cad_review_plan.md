# R01 E05 - parametric CAD review plan
Existing OpenSCAD camera, pan-tilt and pad frame concepts are unrendered and unfit-tested. Units are millimetres; hardware datums and real mounting dimensions must be measured. Future designs must specify min/max parameters, hole clearance, edge distance, wall thickness, fastener head/tool access, print orientation, mass and support strategy.

Use parameter assertions to reject negative dimensions, overlapping holes and impossible clearances. Render at minimum, nominal and maximum settings. CAD assertions verify geometry assumptions only; they do not verify strength, fatigue, thermal distortion or fastening loads.

A printed camera bracket can alter calibration when it flexes. Measure loaded deflection and vibration before assigning extrinsics. No part is flight-qualified by this review.
