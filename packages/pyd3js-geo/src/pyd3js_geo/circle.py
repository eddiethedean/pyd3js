"""geoCircle generator (d3-geo `circle.js` implementation in `_circle_geo`)."""

from __future__ import annotations

from pyd3js_geo._circle_geo import geo_circle_factory


def geoCircle():
    return geo_circle_factory()
