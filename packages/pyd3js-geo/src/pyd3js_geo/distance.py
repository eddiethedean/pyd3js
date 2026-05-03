"""Great-circle distance (d3-geo `distance.js`)."""

from __future__ import annotations

from collections.abc import Sequence

from pyd3js_geo.length import geoLength


def geoDistance(a: Sequence[float], b: Sequence[float]) -> float:
    return geoLength({"type": "LineString", "coordinates": [a, b]})
