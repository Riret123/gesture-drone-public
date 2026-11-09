# R04 E01 - planar mounting checker
`sensor_mount_geometry` validates rectangular plate dimensions and circular-hole centre tuples in millimetres using a lower-left datum. Positive finite dimensions are required. Edge clearance is measured from hole edge, not centre; hole gap is edge-to-edge. Exact clearance boundaries pass. Duplicates or insufficient spacing create indexed findings.

A concept bound of 64 holes limits quadratic pair checking and is disclosed as a software resource choice, not a mechanical safety value. Invalid data and numerical overflow raise errors. All geometric findings are returned together when input is otherwise valid.

No thickness, loads, print orientation, material, fastener head/tool access or camera fit is validated. Existing CAD files are unchanged.
