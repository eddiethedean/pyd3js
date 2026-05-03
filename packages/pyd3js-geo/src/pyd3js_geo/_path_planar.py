"""Planar path streams for projected coordinates (d3-geo `path/*.js`)."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_array import Adder


def _noop(*_a: Any, **_k: Any) -> None:
    return None


class PathBoundsStream:
    __slots__ = ("x0", "y0", "x1", "y1")

    def __init__(self) -> None:
        self.x0 = self.y0 = math.inf
        self.x1 = self.y1 = -math.inf

    def point(self, x: float, y: float, _z: Any = None) -> None:
        if x < self.x0:
            self.x0 = x
        if x > self.x1:
            self.x1 = x
        if y < self.y0:
            self.y0 = y
        if y > self.y1:
            self.y1 = y

    lineStart = lineEnd = polygonStart = polygonEnd = _noop

    def sphere(self) -> None:
        pass

    def result(self) -> list[list[float]]:
        b = [[self.x0, self.y0], [self.x1, self.y1]]
        self.x0 = self.y0 = math.inf
        self.x1 = self.y1 = -math.inf
        return b


class PathAreaStream:
    """path/area.js — planar ring areas."""

    __slots__ = ("area_sum", "area_ring_sum", "x00", "y00", "x0", "y0", "point", "lineStart", "lineEnd")

    def __init__(self) -> None:
        self.area_sum = Adder()
        self.area_ring_sum = Adder()
        self.x00 = self.y00 = self.x0 = self.y0 = 0.0
        self.point = _noop
        self.lineStart = _noop
        self.lineEnd = _noop

    def polygonStart(self) -> None:
        self.lineStart = self._area_ring_start
        self.lineEnd = self._area_ring_end

    def polygonEnd(self) -> None:
        self.lineStart = self.lineEnd = self.point = _noop
        self.area_sum.add(abs(float(self.area_ring_sum)))
        self.area_ring_sum = Adder()

    def _area_ring_start(self) -> None:
        self.point = self._area_point_first

    def _area_point_first(self, x: float, y: float, _z: Any = None) -> None:
        self.point = self._area_point
        self.x00 = self.x0 = x
        self.y00 = self.y0 = y

    def _area_point(self, x: float, y: float, _z: Any = None) -> None:
        self.area_ring_sum.add(self.y0 * x - self.x0 * y)
        self.x0, self.y0 = x, y

    def _area_ring_end(self) -> None:
        self._area_point(self.x00, self.y00)

    def sphere(self) -> None:
        pass

    def result(self) -> float:
        a = float(self.area_sum) / 2
        self.area_sum = Adder()
        return a


class PathMeasureStream:
    """path/measure.js"""

    __slots__ = (
        "length_sum",
        "length_ring",
        "x00",
        "y00",
        "x0",
        "y0",
        "point",
        "lineStart",
        "lineEnd",
        "polygonStart",
        "polygonEnd",
    )

    def __init__(self) -> None:
        self.length_sum = Adder()
        self.length_ring = False
        self.x00 = self.y00 = self.x0 = self.y0 = 0.0
        self.point = _noop
        self.lineStart = self._line_start
        self.lineEnd = self._line_end

        def ps() -> None:
            self.length_ring = True

        def pe() -> None:
            self.length_ring = False

        self.polygonStart = ps
        self.polygonEnd = pe

    def _line_start(self) -> None:
        self.point = self._length_point_first

    def _line_end(self) -> None:
        if self.length_ring:
            self._length_point(self.x00, self.y00)
        self.point = _noop

    def _length_point_first(self, x: float, y: float, _z: Any = None) -> None:
        self.point = self._length_point
        self.x00 = self.x0 = x
        self.y00 = self.y0 = y

    def _length_point(self, x: float, y: float, _z: Any = None) -> None:
        dx = self.x0 - x
        dy = self.y0 - y
        self.length_sum.add(math.hypot(dx, dy))
        self.x0, self.y0 = x, y

    def sphere(self) -> None:
        pass

    def result(self) -> float:
        total = float(self.length_sum)
        self.length_sum = Adder()
        return total


class PathCentroidStream:
    """path/centroid.js — planar centroid."""

    __slots__ = (
        "X0",
        "Y0",
        "Z0",
        "X1",
        "Y1",
        "Z1",
        "X2",
        "Y2",
        "Z2",
        "x00",
        "y00",
        "x0",
        "y0",
        "point",
        "lineStart",
        "lineEnd",
    )

    def __init__(self) -> None:
        self.X0 = self.Y0 = self.Z0 = 0.0
        self.X1 = self.Y1 = self.Z1 = 0.0
        self.X2 = self.Y2 = self.Z2 = 0.0
        self.x00 = self.y00 = 0.0
        self.x0 = self.y0 = 0.0
        self.point = self._centroid_point
        self.lineStart = self._centroid_line_start
        self.lineEnd = self._centroid_line_end

    def polygonStart(self) -> None:
        self.lineStart = self._centroid_ring_start
        self.lineEnd = self._centroid_ring_end

    def polygonEnd(self) -> None:
        self.point = self._centroid_point
        self.lineStart = self._centroid_line_start
        self.lineEnd = self._centroid_line_end

    def sphere(self) -> None:
        pass

    def _centroid_point(self, x: float, y: float, _z: Any = None) -> None:
        self.X0 += x
        self.Y0 += y
        self.Z0 += 1

    def _centroid_line_start(self) -> None:
        self.point = self._centroid_line_point_first

    def _centroid_line_point_first(self, x: float, y: float, _z: Any = None) -> None:
        self.point = self._centroid_line_point
        self.x0, self.y0 = x, y
        self._centroid_point(x, y)

    def _centroid_line_point(self, x: float, y: float, _z: Any = None) -> None:
        dx = x - self.x0
        dy = y - self.y0
        z = math.hypot(dx, dy)
        self.X1 += z * (self.x0 + x) / 2
        self.Y1 += z * (self.y0 + y) / 2
        self.Z1 += z
        self._centroid_point(x, y)
        self.x0, self.y0 = x, y

    def _centroid_line_end(self) -> None:
        self.point = self._centroid_point

    def _centroid_ring_start(self) -> None:
        self.point = self._centroid_ring_point_first

    def _centroid_ring_end(self) -> None:
        self._centroid_ring_point(self.x00, self.y00)
        self.point = self._centroid_point

    def _centroid_ring_point_first(self, x: float, y: float, _z: Any = None) -> None:
        self.point = self._centroid_ring_point
        self.x00 = self.x0 = x
        self.y00 = self.y0 = y
        self._centroid_point(x, y)

    def _centroid_ring_point(self, x: float, y: float, _z: Any = None) -> None:
        dx = x - self.x0
        dy = y - self.y0
        zlen = math.hypot(dx, dy)
        self.X1 += zlen * (self.x0 + x) / 2
        self.Y1 += zlen * (self.y0 + y) / 2
        self.Z1 += zlen
        zz = self.y0 * x - self.x0 * y
        self.X2 += zz * (self.x0 + x)
        self.Y2 += zz * (self.y0 + y)
        self.Z2 += zz * 3
        self._centroid_point(x, y)
        self.x0, self.y0 = x, y

    def result(self) -> list[float]:
        if self.Z2:
            out = [self.X2 / self.Z2, self.Y2 / self.Z2]
        elif self.Z1:
            out = [self.X1 / self.Z1, self.Y1 / self.Z1]
        elif self.Z0:
            out = [self.X0 / self.Z0, self.Y0 / self.Z0]
        else:
            out = [math.nan, math.nan]
        self.X0 = self.Y0 = self.Z0 = 0.0
        self.X1 = self.Y1 = self.Z1 = 0.0
        self.X2 = self.Y2 = self.Z2 = 0.0
        return out


class PathContext:
    """path/context.js — maps geo stream to Canvas/SVG-like commands."""

    __slots__ = ("_context", "_line", "_point", "_radius")

    def __init__(self, context: Any) -> None:
        self._context = context
        # NaN = planar LineString; 0 = first polygon ring (d3-geo path/context.js).
        self._line = math.nan
        self._point = math.nan
        self._radius = 4.5

    def pointRadius(self, r: float) -> PathContext:
        self._radius = float(r)
        return self

    def polygonStart(self) -> None:
        self._line = 0.0

    def polygonEnd(self) -> None:
        self._line = math.nan

    def lineStart(self) -> None:
        self._point = 0.0

    def lineEnd(self) -> None:
        if self._line == 0:
            self._context.closePath()
        self._point = math.nan

    def point(self, x: float, y: float, _z: Any = None) -> None:
        if self._point == 0:
            self._context.moveTo(x, y)
            self._point = 1
        elif self._point == 1:
            self._context.lineTo(x, y)
        else:
            r = self._radius
            self._context.moveTo(x + r, y)
            self._context.arc(x, y, r, 0, 2 * math.pi)

    def result(self) -> None:
        return None
