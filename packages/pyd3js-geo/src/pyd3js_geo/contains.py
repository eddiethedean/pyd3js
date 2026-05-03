"""Point-in-geometry tests (d3-geo `contains.js`)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from pyd3js_geo.distance import geoDistance
from pyd3js_geo.math import epsilon2, radians
from pyd3js_geo.polygon_contains import polygon_contains_rings


def _ring_radians(ring: list[list[float]]) -> list[list[float]]:
    out = [[p[0] * radians, p[1] * radians] for p in ring]
    out.pop()
    return out


def _contains_line(coords: list[list[float]], point: Sequence[float]) -> bool:
    ao: float | None = None
    for i, c in enumerate(coords):
        bo = geoDistance(c, point)
        if bo == 0:
            return True
        if i > 0:
            ab = geoDistance(coords[i], coords[i - 1])
            if (
                ab > 0
                and ao is not None
                and ao <= ab
                and bo <= ab
                and (ao + bo - ab) * (1 - ((ao - bo) / ab) ** 2) < epsilon2 * ab
            ):
                return True
        ao = bo
    return False


def _contains_polygon_coords(
    coordinates: list[list[list[float]]], point: Sequence[float]
) -> bool:
    rings = [_ring_radians(r) for r in coordinates]
    pr = [point[0] * radians, point[1] * radians]
    return polygon_contains_rings(rings, pr)


def geoContains(obj: Any, point: Sequence[float]) -> bool:
    typ = obj.get("type") if obj else None
    if typ == "Sphere":
        return True
    if typ == "Feature":
        return geoContains(obj.get("geometry"), point)
    if typ == "FeatureCollection":
        return any(
            geoContains(f.get("geometry"), point) for f in obj.get("features", [])
        )
    if typ == "Point":
        return geoDistance(obj.get("coordinates"), point) == 0
    if typ == "MultiPoint":
        return any(geoDistance(c, point) == 0 for c in obj.get("coordinates", []))
    if typ == "LineString":
        return _contains_line(obj.get("coordinates", []), point)
    if typ == "MultiLineString":
        return any(_contains_line(line, point) for line in obj.get("coordinates", []))
    if typ == "Polygon":
        return _contains_polygon_coords(obj.get("coordinates", []), point)
    if typ == "MultiPolygon":
        return any(
            _contains_polygon_coords(p, point) for p in obj.get("coordinates", [])
        )
    if typ == "GeometryCollection":
        return any(geoContains(g, point) for g in obj.get("geometries", []))
    return False
