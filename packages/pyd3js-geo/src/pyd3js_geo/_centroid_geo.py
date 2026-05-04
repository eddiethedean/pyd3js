"""Spherical centroid (d3-geo `centroid.js`)."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_array import Adder

epsilon = 1e-6
epsilon2 = 1e-12
degrees = 180 / math.pi
radians = math.pi / 180


class GeoCentroidStream:
    __slots__ = (
        "w0",
        "w1",
        "x0",
        "y0",
        "z0",
        "x1",
        "y1",
        "z1",
        "x2",
        "y2",
        "z2",
        "_lambda00",
        "_phi00",
        "_x0",
        "_y0",
        "_z0",
        "point",
        "lineStart",
        "lineEnd",
    )

    def __init__(self) -> None:
        self.w0 = self.w1 = 0.0
        self.x0 = self.y0 = self.z0 = 0.0
        self.x1 = self.y1 = self.z1 = 0.0
        self.x2 = Adder()
        self.y2 = Adder()
        self.z2 = Adder()
        self._lambda00 = self._phi00 = 0.0
        self._x0 = self._y0 = self._z0 = 0.0
        self.point = self._centroid_point
        self.lineStart = self._centroid_line_start
        self.lineEnd = self._centroid_line_end

    def sphere(self) -> None:
        pass

    def polygonStart(self) -> None:
        self.lineStart = self._centroid_ring_start
        self.lineEnd = self._centroid_ring_end

    def polygonEnd(self) -> None:
        self.lineStart = self._centroid_line_start
        self.lineEnd = self._centroid_line_end

    def _centroid_point_cartesian(self, x: float, y: float, z: float) -> None:
        self.w0 += 1
        self.x0 += (x - self.x0) / self.w0
        self.y0 += (y - self.y0) / self.w0
        self.z0 += (z - self.z0) / self.w0

    def _centroid_point(self, lam: float, phi: float, _z: Any = None) -> None:
        lam *= radians
        phi *= radians
        cp = math.cos(phi)
        self._centroid_point_cartesian(cp * math.cos(lam), cp * math.sin(lam), math.sin(phi))

    def _centroid_line_start(self) -> None:
        self.point = self._centroid_line_point_first

    def _centroid_line_point_first(self, lam: float, phi: float, _z: Any = None) -> None:
        lam *= radians
        phi *= radians
        cp = math.cos(phi)
        self._x0 = cp * math.cos(lam)
        self._y0 = cp * math.sin(lam)
        self._z0 = math.sin(phi)
        self.point = self._centroid_line_point
        self._centroid_point_cartesian(self._x0, self._y0, self._z0)

    def _centroid_line_point(self, lam: float, phi: float, _z: Any = None) -> None:
        lam *= radians
        phi *= radians
        cp = math.cos(phi)
        x = cp * math.cos(lam)
        y = cp * math.sin(lam)
        z = math.sin(phi)
        cx = self._y0 * z - self._z0 * y
        cy = self._z0 * x - self._x0 * z
        cz = self._x0 * y - self._y0 * x
        w = math.atan2(
            math.sqrt(cx * cx + cy * cy + cz * cz),
            self._x0 * x + self._y0 * y + self._z0 * z,
        )
        self.w1 += w
        self.x1 += w * (self._x0 + x)
        self.y1 += w * (self._y0 + y)
        self.z1 += w * (self._z0 + z)
        self._x0, self._y0, self._z0 = x, y, z
        self._centroid_point_cartesian(x, y, z)

    def _centroid_line_end(self) -> None:
        self.point = self._centroid_point

    def _centroid_ring_start(self) -> None:
        self.point = self._centroid_ring_point_first

    def _centroid_ring_end(self) -> None:
        self._centroid_ring_point(self._lambda00, self._phi00)
        self.point = self._centroid_point

    def _centroid_ring_point_first(self, lam: float, phi: float, _z: Any = None) -> None:
        self._lambda00, self._phi00 = lam, phi
        lam *= radians
        phi *= radians
        self.point = self._centroid_ring_point
        cp = math.cos(phi)
        self._x0 = cp * math.cos(lam)
        self._y0 = cp * math.sin(lam)
        self._z0 = math.sin(phi)
        self._centroid_point_cartesian(self._x0, self._y0, self._z0)

    def _centroid_ring_point(self, lam: float, phi: float, _z: Any = None) -> None:
        lam *= radians
        phi *= radians
        cp = math.cos(phi)
        x = cp * math.cos(lam)
        y = cp * math.sin(lam)
        z = math.sin(phi)
        cx = self._y0 * z - self._z0 * y
        cy = self._z0 * x - self._x0 * z
        cz = self._x0 * y - self._y0 * x
        m = math.hypot(cx, cy, cz)
        w_arc = math.asin(m)
        v = (-w_arc / m) if m else 0.0
        self.x2.add(v * cx)
        self.y2.add(v * cy)
        self.z2.add(v * cz)
        self.w1 += w_arc
        self.x1 += w_arc * (self._x0 + x)
        self.y1 += w_arc * (self._y0 + y)
        self.z1 += w_arc * (self._z0 + z)
        self._x0, self._y0, self._z0 = x, y, z
        self._centroid_point_cartesian(x, y, z)


def geo_centroid_from_stream(obj: Any) -> list[float]:
    from pyd3js_geo.stream import geoStream

    s = GeoCentroidStream()
    geoStream(obj, s)
    x = float(s.x2)
    y = float(s.y2)
    z = float(s.z2)
    m = math.hypot(x, y, z)
    if m < epsilon2:
        x, y, z = s.x1, s.y1, s.z1
        if s.w1 < epsilon:
            x, y, z = s.x0, s.y0, s.z0
        m = math.hypot(x, y, z)
        if m < epsilon2:
            return [math.nan, math.nan]
    return [math.atan2(y, x) * degrees, math.asin(z / m) * degrees]
