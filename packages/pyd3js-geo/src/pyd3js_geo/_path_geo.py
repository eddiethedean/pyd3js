"""Planar geo path (d3-geo `path/index.js`)."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_geo._path_planar import (
    PathAreaStream,
    PathBoundsStream,
    PathCentroidStream,
    PathContext,
    PathMeasureStream,
)
from pyd3js_geo.stream import geoStream

_MISSING = object()


def _fmt(x: float, digits: int | None) -> str:
    if digits is not None:
        k = 10**digits
        x = (math.floor(x * k + 0.5) if x >= 0 else math.ceil(x * k - 0.5)) / k
    return format(0 if x == 0 else x, ".15g")


class PathString:
    def __init__(self, digits: int | None = 3):
        self._digits, self._radius, self._, self._line, self._point = (
            digits,
            4.5,
            "",
            math.nan,
            math.nan,
        )

    def pointRadius(self, r):
        self._radius = float(r)
        return self

    def polygonStart(self):
        self._line = 0

    def polygonEnd(self):
        self._line = math.nan

    def lineStart(self):
        self._point = 0

    def lineEnd(self):
        if self._line == 0:
            self._ += "Z"
        self._point = math.nan

    def point(self, x, y, z=None):
        if self._point == 0:
            self._ += f"M{_fmt(x, self._digits)},{_fmt(y, self._digits)}"
            self._point = 1
        elif self._point == 1:
            self._ += f"L{_fmt(x, self._digits)},{_fmt(y, self._digits)}"
        else:
            r = self._radius
            self._ += f"M{_fmt(x, self._digits)},{_fmt(y, self._digits)}m0,{_fmt(r, self._digits)}a{_fmt(r, self._digits)},{_fmt(r, self._digits)} 0 1,1 0,{_fmt(-2 * r, self._digits)}a{_fmt(r, self._digits)},{_fmt(r, self._digits)} 0 1,1 0,{_fmt(2 * r, self._digits)}z"

    def result(self):
        r = self._
        self._ = ""
        return r or None


class GeoPath:
    """Matches d3 `path/index.js` (planar metrics vs spherical geo* helpers)."""

    def __init__(self, projection: Any = None, context: Any = None):
        self._projection = projection
        self._digits = 3
        self._point_radius: Any = 4.5
        self._context = context
        self._context_stream: Any = None
        self._sync_context_stream()

    def _sync_context_stream(self) -> None:
        if self._context is None:
            ps = PathString(self._digits)
            if not callable(self._point_radius):
                ps.pointRadius(float(self._point_radius))
            self._context_stream = ps
        else:
            pc = PathContext(self._context)
            if not callable(self._point_radius):
                pc.pointRadius(float(self._point_radius))
            self._context_stream = pc

    def __call__(self, obj: Any = None):
        if obj:
            stream = (
                self._projection.stream(self._context_stream)
                if self._projection is not None
                else self._context_stream
            )
            geoStream(obj, stream)
        return self._context_stream.result()

    def projection(self, v: Any = _MISSING):
        if v is _MISSING:
            return self._projection
        self._projection = v
        return self

    def context(self, v: Any = _MISSING):
        if v is _MISSING:
            return self._context
        self._context = v
        self._sync_context_stream()
        return self

    def pointRadius(self, v: Any = _MISSING):
        if v is _MISSING:
            return self._point_radius
        self._point_radius = v
        self._sync_context_stream()
        if self._context is not None and not callable(v):
            if hasattr(self._context_stream, "pointRadius"):
                self._context_stream.pointRadius(float(v))
        return self

    def digits(self, v: Any = _MISSING):
        if v is _MISSING:
            return self._digits
        self._digits = None if v is None else int(math.floor(v))
        if self._context is None:
            ps = PathString(self._digits)
            if not callable(self._point_radius):
                ps.pointRadius(float(self._point_radius))
            self._context_stream = ps
        return self

    def area(self, obj: Any) -> float:
        s = PathAreaStream()
        geoStream(
            obj,
            self._projection.stream(s) if self._projection is not None else s,
        )
        return s.result()

    def measure(self, obj: Any) -> float:
        s = PathMeasureStream()
        geoStream(
            obj,
            self._projection.stream(s) if self._projection is not None else s,
        )
        return s.result()

    def bounds(self, obj: Any) -> list[list[float]]:
        s = PathBoundsStream()
        geoStream(
            obj,
            self._projection.stream(s) if self._projection is not None else s,
        )
        return s.result()

    def centroid(self, obj: Any) -> list[float]:
        s = PathCentroidStream()
        geoStream(
            obj,
            self._projection.stream(s) if self._projection is not None else s,
        )
        return s.result()


def geoPath(projection: Any = None, context: Any = None) -> GeoPath:
    return GeoPath(projection, context)
