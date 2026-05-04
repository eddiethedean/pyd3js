"""Spherical bounds (d3-geo `bounds.js`)."""

from __future__ import annotations

import math
from typing import Any

from pyd3js_array import Adder

from pyd3js_geo._geo_area_stream import GeoAreaStream
from pyd3js_geo.cartesian import (
    cartesian,
    cartesian_cross,
    cartesian_normalize_in_place,
    spherical,
)

epsilon = 1e-6
degrees = 180 / math.pi
radians = math.pi / 180


def _abs(x: float) -> float:
    return abs(x)


def angle(la0: float, la1: float) -> float:
    d = la1 - la0
    return d + 360 if d < 0 else d


def range_compare(a: list[float], b: list[float]) -> float:
    return a[0] - b[0]


def range_contains(rng: list[float], x: float) -> bool:
    return rng[0] <= x <= rng[1] if rng[0] <= rng[1] else (x < rng[0] or rng[1] < x)


class _BoundsState:
    __slots__ = (
        "lambda0",
        "phi0",
        "lambda1",
        "phi1",
        "lambda2",
        "lambda00",
        "phi00",
        "p0",
        "delta_sum",
        "ranges",
        "range",
        "area_stream",
        "point",
        "lineStart",
        "lineEnd",
    )

    def __init__(self, area_stream: GeoAreaStream) -> None:
        self.lambda0 = math.inf
        self.phi0 = math.inf
        self.lambda1 = -math.inf
        self.phi1 = -math.inf
        self.lambda2 = 0.0
        self.lambda00 = self.phi00 = 0.0
        self.p0: list[float] | None = None
        self.delta_sum = Adder()
        self.ranges: list[list[float]] = []
        self.range: list[float] | None = None
        self.area_stream = area_stream
        self.point = self.bounds_point
        self.lineStart = self.bounds_line_start
        self.lineEnd = self.bounds_line_end

    def bounds_point(self, lam: float, phi: float, _z: Any = None) -> None:
        self.lambda0 = self.lambda1 = lam
        self.range = [lam, lam]
        self.ranges.append(self.range)
        if phi < self.phi0:
            self.phi0 = phi
        if phi > self.phi1:
            self.phi1 = phi

    def line_point(self, lam: float, phi: float, _z: Any = None) -> None:
        p = cartesian([lam * radians, phi * radians])
        if self.p0 is not None:
            normal = cartesian_cross(self.p0, p)
            equatorial = [normal[1], -normal[0], 0.0]
            inflection = cartesian_cross(equatorial, normal)
            cartesian_normalize_in_place(inflection)
            inflection = spherical(inflection)
            delta = lam - self.lambda2
            sign = 1.0 if delta > 0 else -1.0
            lambdai = inflection[0] * degrees * sign
            antimeridian = _abs(delta) > 180
            if antimeridian ^ (sign * self.lambda2 < lambdai < sign * lam):
                phii = inflection[1] * degrees
                if phii > self.phi1:
                    self.phi1 = phii
            else:
                lambdai = (lambdai + 360) % 360 - 180
                if antimeridian ^ (sign * self.lambda2 < lambdai < sign * lam):
                    phii = -inflection[1] * degrees
                    if phii < self.phi0:
                        self.phi0 = phii
                else:
                    if phi < self.phi0:
                        self.phi0 = phi
                    if phi > self.phi1:
                        self.phi1 = phi
            if antimeridian:
                if lam < self.lambda2:
                    if angle(self.lambda0, lam) > angle(self.lambda0, self.lambda1):
                        self.lambda1 = lam
                else:
                    if angle(lam, self.lambda1) > angle(self.lambda0, self.lambda1):
                        self.lambda0 = lam  # pragma: no cover
            else:
                if self.lambda1 >= self.lambda0:
                    if lam < self.lambda0:
                        self.lambda0 = lam
                    if lam > self.lambda1:
                        self.lambda1 = lam
                else:
                    if lam > self.lambda2:
                        if angle(self.lambda0, lam) > angle(self.lambda0, self.lambda1):
                            self.lambda1 = lam
                    else:
                        if angle(lam, self.lambda1) > angle(
                            self.lambda0, self.lambda1
                        ):  # pragma: no cover
                            self.lambda0 = lam  # pragma: no cover
        else:
            self.lambda0 = self.lambda1 = lam
            self.range = [lam, lam]
            self.ranges.append(self.range)
        if phi < self.phi0:
            self.phi0 = phi
        if phi > self.phi1:
            self.phi1 = phi
        self.p0 = p
        self.lambda2 = lam

    def bounds_line_start(self) -> None:
        self.point = self.line_point

    def bounds_line_end(self) -> None:
        assert self.range is not None
        self.range[0] = self.lambda0
        self.range[1] = self.lambda1
        self.point = self.bounds_point
        self.p0 = None

    def bounds_ring_point(self, lam: float, phi: float, _z: Any = None) -> None:
        if self.p0 is not None:
            delta = lam - self.lambda2
            self.delta_sum.add(
                delta + (360 if delta > 0 else -360) if _abs(delta) > 180 else delta
            )
        else:
            self.lambda00 = lam
            self.phi00 = phi
        self.area_stream.point(lam, phi)
        self.line_point(lam, phi)

    def bounds_ring_start(self) -> None:
        self.area_stream.lineStart()

    def bounds_ring_end(self) -> None:
        self.bounds_ring_point(self.lambda00, self.phi00)
        self.area_stream.lineEnd()
        if _abs(float(self.delta_sum)) > epsilon:
            self.lambda0 = -180.0
            self.lambda1 = 180.0
        assert self.range is not None
        self.range[0] = self.lambda0
        self.range[1] = self.lambda1
        self.p0 = None

    def polygon_start(self) -> None:
        self.point = self.bounds_ring_point
        self.lineStart = self.bounds_ring_start
        self.lineEnd = self.bounds_ring_end
        self.delta_sum = Adder()
        self.area_stream.polygonStart()

    def polygon_end(self) -> None:
        self.area_stream.polygonEnd()
        self.point = self.bounds_point
        self.lineStart = self.bounds_line_start
        self.lineEnd = self.bounds_line_end
        ars = float(self.area_stream.area_ring_sum)
        if ars < 0:
            self.lambda0 = -180.0
            self.lambda1 = 180.0
            self.phi0 = -90.0
            self.phi1 = 90.0
        elif float(self.delta_sum) > epsilon:
            self.phi1 = 90.0  # pragma: no cover
        elif float(self.delta_sum) < -epsilon:
            self.phi0 = -90.0
        assert self.range is not None
        self.range[0] = self.lambda0
        self.range[1] = self.lambda1

    def sphere(self) -> None:
        self.lambda0 = -180.0
        self.lambda1 = 180.0
        self.phi0 = -90.0
        self.phi1 = 90.0


def geo_bounds_from_stream(feature: Any) -> list[list[float]]:
    from pyd3js_geo.stream import geoStream

    bs = _BoundsState(GeoAreaStream())

    class Stream:
        def point(self, x: float, y: float, z: Any = None) -> None:
            bs.point(x, y, z)

        def lineStart(self) -> None:
            bs.lineStart()

        def lineEnd(self) -> None:
            bs.lineEnd()

        def polygonStart(self) -> None:
            bs.polygon_start()

        def polygonEnd(self) -> None:
            bs.polygon_end()

        def sphere(self) -> None:
            bs.sphere()

    geoStream(feature, Stream())

    ranges = bs.ranges
    if not ranges:
        if bs.lambda0 != math.inf and bs.lambda1 != -math.inf:
            return [[bs.lambda0, bs.phi0], [bs.lambda1, bs.phi1]]
        return [[math.nan, math.nan], [math.nan, math.nan]]

    lambda0_out = lambda1_out = 0.0
    if ranges:
        ranges.sort(key=lambda r: r[0])
        merged = [ranges[0]]
        a = merged[0]
        for i in range(1, len(ranges)):
            b = ranges[i]
            if range_contains(a, b[0]) or range_contains(a, b[1]):
                if angle(a[0], b[1]) > angle(a[0], a[1]):  # pragma: no cover
                    a[1] = b[1]  # pragma: no cover
                if angle(b[0], a[1]) > angle(a[0], a[1]):  # pragma: no cover
                    a[0] = b[0]  # pragma: no cover
            else:
                merged.append(b)
                a = b

        n = len(merged) - 1
        delta_max = -math.inf
        aa = merged[n]
        for i in range(n + 1):
            bb = merged[i]
            d = angle(aa[1], bb[0])
            if d > delta_max:
                delta_max = d
                lambda0_out = bb[0]
                lambda1_out = aa[1]
            aa = bb

    if bs.lambda0 == math.inf or bs.phi0 == math.inf:
        return [[math.nan, math.nan], [math.nan, math.nan]]  # pragma: no cover
    return [[lambda0_out, bs.phi0], [lambda1_out, bs.phi1]]
