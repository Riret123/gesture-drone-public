"""Offline circular fastener/tool access envelopes on planar plate concepts."""
import math
from .sensor_mount_geometry import MountGeometry, validate_mount
from .validation import finite


def check_access(geometry: MountGeometry, *, head_diameter_mm: float,
                 tool_diameter_mm: float, access_clearance_mm: float) -> tuple:
    """Return base hole geometry and conservative circular access findings.

    Model requires the entire circular head/tool envelope to stay inside plate;
    no protruding access, 3D tool approach, obstacles or fastener threads modeled.
    """
    findings = list(validate_mount(geometry))
    if not all(finite(v) and v > 0 for v in
               (head_diameter_mm, tool_diameter_mm, access_clearance_mm)):
        raise ValueError('positive finite access dimensions required')
    if head_diameter_mm < geometry.hole_diameter_mm:
        raise ValueError('head diameter cannot be smaller than through-hole in this model')
    diameter = max(head_diameter_mm, tool_diameter_mm)
    radius = diameter / 2 + access_clearance_mm
    spacing = diameter + access_clearance_mm
    if not math.isfinite(radius) or not math.isfinite(spacing):
        raise ValueError('access geometry arithmetic overflow')
    for index, (x, y) in enumerate(geometry.holes_xy_mm):
        if not radius <= x <= geometry.width_mm - radius or not radius <= y <= geometry.height_mm - radius:
            findings.append(('access_edge_clearance', index))
    for first in range(len(geometry.holes_xy_mm)):
        for second in range(first + 1, len(geometry.holes_xy_mm)):
            if math.dist(geometry.holes_xy_mm[first], geometry.holes_xy_mm[second]) < spacing:
                findings.append(('access_overlap', first, second))
    return tuple(findings)
