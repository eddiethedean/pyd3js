"""Shim for d3-geo `pointEqual.js` — implementation in `_point_equal`."""

from pyd3js_geo._point_equal import epsilon, point_equal

__all__ = ["epsilon", "point_equal"]
