"""Millimetre-only planar mounting geometry checks, not structural validation."""
from dataclasses import dataclass
import math
from .validation import finite


@dataclass(frozen=True)
class MountGeometry:
    width_mm: float
    height_mm: float
    hole_diameter_mm: float
    edge_clearance_mm: float
    hole_gap_mm: float
    holes_xy_mm: tuple


def validate_mount(geometry: MountGeometry) -> tuple:
    """Return all geometric findings; hole centres use lower-left plate datum.

    Clearance is edge-to-hole-edge and gap is hole-edge-to-hole-edge. No material,
    loads, print settings, fastener head clearance or manufacturing fit is modeled.
    """
    if not isinstance(geometry, MountGeometry):
        raise ValueError('mount geometry required')
    g = geometry
    if not all(finite(v) and v > 0 for v in
               (g.width_mm, g.height_mm, g.hole_diameter_mm,
                g.edge_clearance_mm, g.hole_gap_mm)):
        raise ValueError('positive finite dimensions in millimetres required')
    if type(g.holes_xy_mm) is not tuple or not g.holes_xy_mm:
        raise ValueError('nonempty tuple of explicit hole centres required')
    if len(g.holes_xy_mm) > 64:
        raise ValueError('hole count exceeds concept validation limit')
    for centre in g.holes_xy_mm:
        if (type(centre) is not tuple or len(centre) != 2
                or not all(finite(v) for v in centre)):
            raise ValueError('finite XY centre tuples required')
    findings = []
    margin = g.hole_diameter_mm / 2 + g.edge_clearance_mm
    if not math.isfinite(margin):
        raise ValueError('dimension arithmetic overflow')
    for index, (x, y) in enumerate(g.holes_xy_mm):
        if not margin <= x <= g.width_mm - margin or not margin <= y <= g.height_mm - margin:
            findings.append(('edge_clearance', index))
    separation = g.hole_diameter_mm + g.hole_gap_mm
    if not math.isfinite(separation):
        raise ValueError('dimension arithmetic overflow')
    for first in range(len(g.holes_xy_mm)):
        for second in range(first + 1, len(g.holes_xy_mm)):
            distance = math.dist(g.holes_xy_mm[first], g.holes_xy_mm[second])
            if not math.isfinite(distance):
                raise ValueError('hole distance arithmetic overflow')
            if distance < separation:
                findings.append(('hole_gap', first, second))
    return tuple(findings)
