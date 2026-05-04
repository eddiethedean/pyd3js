"""Fit projection to GeoJSON (d3-geo `projection/fit.js` helpers)."""

from __future__ import annotations

from typing import Any, Callable

from pyd3js_geo._path_planar import PathBoundsStream
from pyd3js_geo.stream import geoStream


def _fit_bounds_extent(
    projection: Any, extent: list[list[float]], b: list[list[float]]
) -> None:
    w = extent[1][0] - extent[0][0]
    h = extent[1][1] - extent[0][1]
    k = min(w / (b[1][0] - b[0][0]), h / (b[1][1] - b[0][1]))
    x = extent[0][0] + (w - k * (b[1][0] + b[0][0])) / 2
    y = extent[0][1] + (h - k * (b[1][1] + b[0][1])) / 2
    projection.scale(150 * k).translate([x, y])


def _fit_bounds_width(projection: Any, width: float, b: list[list[float]]) -> None:
    w = float(width)
    k = w / (b[1][0] - b[0][0])
    x = (w - k * (b[1][0] + b[0][0])) / 2
    y = -k * b[0][1]
    projection.scale(150 * k).translate([x, y])


def _fit_bounds_height(projection: Any, height: float, b: list[list[float]]) -> None:
    h = float(height)
    k = h / (b[1][1] - b[0][1])
    x = -k * b[0][0]
    y = (h - k * (b[1][1] + b[0][1])) / 2
    projection.scale(150 * k).translate([x, y])


def _fit(
    projection: Any, fit_bounds: Callable[[list[list[float]]], None], obj: Any
) -> Any:
    clip = projection.clipExtent() if hasattr(projection, "clipExtent") else None
    projection.scale(150).translate([0.0, 0.0])
    if clip is not None:
        projection.clipExtent(None)
    bs = PathBoundsStream()
    geoStream(obj, projection.stream(bs))
    fit_bounds(bs.result())
    if clip is not None:
        projection.clipExtent(clip)
    return projection


def fitExtent(projection: Any, extent: list[list[float]], obj: Any):
    return _fit(
        projection,
        lambda b: _fit_bounds_extent(projection, extent, b),
        obj,
    )


def fitSize(projection: Any, size: list[float], obj: Any):
    return fitExtent(projection, [[0, 0], size], obj)


def fitWidth(projection: Any, width: float, obj: Any):
    return _fit(projection, lambda b: _fit_bounds_width(projection, width, b), obj)


def fitHeight(projection: Any, height: float, obj: Any):
    return _fit(projection, lambda b: _fit_bounds_height(projection, height, b), obj)
