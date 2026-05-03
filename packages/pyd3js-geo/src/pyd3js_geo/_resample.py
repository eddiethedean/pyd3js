"""Adaptive resampling along projected segments (d3-geo `projection/resample.js`)."""

from __future__ import annotations

import math
from typing import Any, Callable

from pyd3js_geo.cartesian import cartesian

epsilon = 1e-6
_max_depth = 16
_cos_min_distance = math.cos(30 * math.pi / 180)


def _asin(x: float) -> float:
    return math.pi / 2 if x > 1 else -math.pi / 2 if x < -1 else math.asin(x)


def _atan2(y: float, x: float) -> float:
    return math.atan2(y, x)


def resample_factory(
    project: Callable[[float, float], list[float]], delta2: float
) -> Callable[[Any], Any]:
    if delta2:
        return _resample(project, delta2)
    return _resample_none(project)


def _resample_none(project: Callable[[float, float], list[float]]) -> Callable[[Any], Any]:
    def factory(stream: Any) -> "_ResampleNone":
        return _ResampleNone(project, stream)

    return factory


class _ResampleNone:
    __slots__ = ("project", "stream")

    def __init__(self, project: Callable[[float, float], list[float]], stream: Any) -> None:
        self.project = project
        self.stream = stream

    def point(self, x: float, y: float, z: Any = None) -> None:
        p = self.project(x, y)
        self.stream.point(p[0], p[1])

    def lineStart(self) -> None:
        self.stream.lineStart()

    def lineEnd(self) -> None:
        self.stream.lineEnd()

    def polygonStart(self) -> None:
        self.stream.polygonStart()

    def polygonEnd(self) -> None:
        self.stream.polygonEnd()

    def sphere(self) -> None:
        getattr(self.stream, "sphere", lambda: None)()


def _resample_line_to(
    project: Callable[[float, float], list[float]],
    delta2: float,
    x0: float,
    y0: float,
    lambda0: float,
    a0: float,
    b0: float,
    c0: float,
    x1: float,
    y1: float,
    lambda1: float,
    a1: float,
    b1: float,
    c1: float,
    depth: int,
    stream: Any,
) -> None:
    dx = x1 - x0
    dy = y1 - y0
    d2 = dx * dx + dy * dy
    if d2 > 4 * delta2 and depth > 0:
        depth -= 1
        a = a0 + a1
        b = b0 + b1
        c = c0 + c1
        m = math.sqrt(a * a + b * b + c * c)
        # Match d3: `phi2 = asin(c /= m)` then pass normalized (a/m, b/m, c) to children.
        c /= m
        phi2 = _asin(c)
        lambda2 = (
            (lambda0 + lambda1) / 2
            if abs(abs(c) - 1) < epsilon or abs(lambda0 - lambda1) < epsilon
            else _atan2(b, a)
        )
        p = project(lambda2, phi2)
        x2, y2 = p[0], p[1]
        dx2 = x2 - x0
        dy2 = y2 - y0
        dz = dy * dx2 - dx * dy2
        if (
            dz * dz / d2 > delta2
            or abs((dx * dx2 + dy * dy2) / d2 - 0.5) > 0.3
            or a0 * a1 + b0 * b1 + c0 * c1 < _cos_min_distance
        ):
            na, nb, nc = a / m, b / m, c
            _resample_line_to(
                project,
                delta2,
                x0,
                y0,
                lambda0,
                a0,
                b0,
                c0,
                x2,
                y2,
                lambda2,
                na,
                nb,
                nc,
                depth,
                stream,
            )
            stream.point(x2, y2)
            _resample_line_to(
                project,
                delta2,
                x2,
                y2,
                lambda2,
                na,
                nb,
                nc,
                x1,
                y1,
                lambda1,
                a1,
                b1,
                c1,
                depth,
                stream,
            )


def _resample(project: Callable[[float, float], list[float]], delta2: float) -> Callable[[Any], Any]:
    def factory(stream: Any) -> "_Resample":
        return _Resample(project, delta2, stream)

    return factory


class _Resample:
    __slots__ = (
        "project",
        "delta2",
        "stream",
        "lambda00",
        "x00",
        "y00",
        "a00",
        "b00",
        "c00",
        "lambda0",
        "x0",
        "y0",
        "a0",
        "b0",
        "c0",
        "_in_polygon",
        "_ring_close_pending",
        "_point_kind",
    )

    def __init__(
        self,
        project: Callable[[float, float], list[float]],
        delta2: float,
        stream: Any,
    ) -> None:
        self.project = project
        self.delta2 = delta2
        self.stream = stream
        self.lambda00 = self.x00 = self.y00 = math.nan
        self.a00 = self.b00 = self.c00 = math.nan
        self.lambda0 = self.x0 = self.y0 = math.nan
        self.a0 = self.b0 = self.c0 = math.nan
        self._in_polygon = False
        self._ring_close_pending = False
        self._point_kind = "simple"

    def point(self, x: float, y: float, z: Any = None) -> None:
        if self._point_kind == "simple":
            p = self.project(x, y)
            self.stream.point(p[0], p[1])
        elif self._point_kind == "line":
            self._line_point(x, y)
        else:
            self._ring_first_point(x, y)

    def _plain_line_start(self) -> None:
        self.x0 = math.nan
        self._ring_close_pending = False
        self._point_kind = "line"
        self.stream.lineStart()

    def lineStart(self) -> None:
        if self._in_polygon:
            self._plain_line_start()
            self._point_kind = "ring_first"
        else:
            self._plain_line_start()

    def _line_point(self, lambda_: float, phi: float) -> None:
        c = cartesian([lambda_, phi])
        p = self.project(lambda_, phi)
        _resample_line_to(
            self.project,
            self.delta2,
            self.x0,
            self.y0,
            self.lambda0,
            self.a0,
            self.b0,
            self.c0,
            p[0],
            p[1],
            lambda_,
            c[0],
            c[1],
            c[2],
            _max_depth,
            self.stream,
        )
        self.x0, self.y0 = p[0], p[1]
        self.lambda0, self.a0, self.b0, self.c0 = lambda_, c[0], c[1], c[2]
        self.stream.point(self.x0, self.y0)

    def _plain_line_end(self) -> None:
        self._point_kind = "simple"
        self.stream.lineEnd()

    def lineEnd(self) -> None:
        if self._ring_close_pending:
            _resample_line_to(
                self.project,
                self.delta2,
                self.x0,
                self.y0,
                self.lambda0,
                self.a0,
                self.b0,
                self.c0,
                self.x00,
                self.y00,
                self.lambda00,
                self.a00,
                self.b00,
                self.c00,
                _max_depth,
                self.stream,
            )
            self._ring_close_pending = False
        self._plain_line_end()

    def polygonStart(self) -> None:
        self.stream.polygonStart()
        self._in_polygon = True

    def polygonEnd(self) -> None:
        self.stream.polygonEnd()
        self._in_polygon = False

    def sphere(self) -> None:
        getattr(self.stream, "sphere", lambda: None)()

    def _ring_first_point(self, lambda_: float, phi: float) -> None:
        self.lambda00 = lambda_
        self._line_point(lambda_, phi)
        self.x00, self.y00 = self.x0, self.y0
        self.a00, self.b00, self.c00 = self.a0, self.b0, self.c0
        self._point_kind = "line"
        self._ring_close_pending = True
