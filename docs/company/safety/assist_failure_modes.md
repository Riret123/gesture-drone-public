# R04 S02 - range/flow failure modes
A slanted range beam may strike an object other than the landing plane. Specular/absorbing surfaces can cause missing or false returns. Optical flow can confuse camera rotation, moving texture and translation; a planar assumption fails on relief or moving objects. A quality scalar alone cannot identify these conditions.

The prototype rejects missing model attestations, stale/future receive time, out-of-envelope range/tilt/flow and low/nonfinite quality. This limits numerical misuse but does not validate the physical model. Accepted estimates must remain advisory/offline until synchronized sensor calibration and held-out ground truth exist.

No sensor is read and no landing controller consumes the estimate. A human should not treat unavailable range/flow as proof of safe altitude.
