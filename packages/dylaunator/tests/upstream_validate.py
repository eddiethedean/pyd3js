"""Validation helpers ported from mapbox/delaunator `test/test.js` (v5.0.1)."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dylaunator import Delaunator


def _orient(px: float, py: float, rx: float, ry: float, qx: float, qy: float) -> float:
    l = (ry - py) * (qx - px)
    r = (rx - px) * (qy - py)
    return l - r if abs(l - r) >= 3.3306690738754716e-16 * abs(l + r) else 0.0


def _convex(
    r: list[float],
    q: list[float],
    p: list[float],
) -> bool:
    return (_orient(p[0], p[1], r[0], r[1], q[0], q[1]) or _orient(r[0], r[1], q[0], q[1], p[0], p[1]) or _orient(q[0], q[1], p[0], p[1], r[0], r[1])) >= 0


def _sum_kahan(x: list[float]) -> float:
    s = x[0]
    err = 0.0
    for i in range(1, len(x)):
        k = x[i]
        m = s + k
        err += (s - m + k) if abs(s) >= abs(k) else (k - m + s)
        s = m
    return s + err


def validate(points: list[list[float]], d: Delaunator | None = None) -> None:
    """Assert Delaunay mesh invariants (halfedges, convex hull, area balance)."""
    from dylaunator import Delaunator

    if d is None:
        d = Delaunator.from_points(points)

    halfedges = d.halfedges
    for i in range(len(halfedges)):
        hi = halfedges[i]
        assert hi == -1 or halfedges[hi] == i, "valid halfedge connection"

    if len(d.triangles) == 0:
        return

    hull_areas: list[float] = []
    hlen = len(d.hull)
    for i in range(hlen):
        j = (i - 1) % hlen
        x0, y0 = points[d.hull[j]]
        x, y = points[d.hull[i]]
        hull_areas.append((x - x0) * (y + y0))
        assert _convex(
            points[d.hull[j]],
            points[d.hull[(j + 1) % hlen]],
            points[d.hull[(j + 3) % hlen]],
        ), f"hull should be convex at {j}"
    hull_area = _sum_kahan(hull_areas)

    triangle_areas: list[float] = []
    tr = d.triangles
    for i in range(0, len(tr), 3):
        ax, ay = points[tr[i]]
        bx, by = points[tr[i + 1]]
        cx, cy = points[tr[i + 2]]
        triangle_areas.append(abs((by - ay) * (cx - bx) - (bx - ax) * (cy - by)))
    triangles_area = _sum_kahan(triangle_areas)

    err = abs((hull_area - triangles_area) / hull_area) if hull_area != 0 else 0.0
    assert err <= math.pow(2, -51), f"triangulation should be valid; {err} error"
