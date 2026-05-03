"""Planar rectangle clip (d3-geo `clip/rectangle.js`)."""

from __future__ import annotations

import math
from typing import Any, Callable

from pyd3js_array import merge

from pyd3js_geo.clip._buffer import clip_buffer
from pyd3js_geo.clip._line import clip_line_rect
from pyd3js_geo.clip._rejoin import _Intersection, clip_rejoin

epsilon = 1e-6
clip_max = 1e9
clip_min = -clip_max


def clip_rectangle(x0: float, y0: float, x1: float, y1: float) -> Callable[[Any], Any]:
    def visible(x: float, y: float) -> bool:
        return x0 <= x <= x1 and y0 <= y <= y1

    def corner(p: Any, direction: float) -> int:
        assert p[0] is not None and p[1] is not None
        if abs(p[0] - x0) < epsilon:
            return 0 if direction > 0 else 3
        if abs(p[0] - x1) < epsilon:
            return 2 if direction > 0 else 1
        if abs(p[1] - y0) < epsilon:
            return 1 if direction > 0 else 0
        return 3 if direction > 0 else 2

    def compare_point(a: Any, b: Any) -> float:
        assert a[0] is not None and a[1] is not None and b[0] is not None and b[1] is not None
        ca = corner(a, 1)
        cb = corner(b, 1)
        if ca != cb:
            return float(ca - cb)
        if ca == 0:
            return b[1] - a[1]
        if ca == 1:
            return a[0] - b[0]
        if ca == 2:
            return a[1] - b[1]
        return b[0] - a[0]

    def interpolate(
        from_: list[float] | None,
        to: list[float] | None,
        direction: float,
        stream: Any,
    ) -> None:
        a = 0
        a1 = 0
        if (
            from_ is None
            or to is None
            or (a := corner(from_, direction)) != (a1 := corner(to, direction))
            or (compare_point(from_, to) < 0) ^ (direction > 0)
        ):
            while True:
                stream.point(
                    x0 if a == 0 or a == 3 else x1,
                    y1 if a > 1 else y0,
                )
                a = (a + direction + 4) % 4
                if a == a1:
                    break
        else:
            assert to is not None
            stream.point(to[0], to[1])

    def compare_intersection_rect(aa: _Intersection, bb: _Intersection) -> int:
        d = compare_point(aa.x, bb.x)
        return (d > 0) - (d < 0)

    def factory(stream: Any) -> "_RectangleClip":
        return _RectangleClip(
            stream,
            x0,
            y0,
            x1,
            y1,
            visible,
            interpolate,
            compare_intersection_rect,
        )

    return factory


class _RectangleClip:
    __slots__ = (
        "stream",
        "x0",
        "y0",
        "x1",
        "y1",
        "visible",
        "interpolate",
        "compare_intersection",
        "active_stream",
        "buffer_stream",
        "segments",
        "polygon",
        "ring",
        "x__",
        "y__",
        "v__",
        "x_",
        "y_",
        "v_",
        "first",
        "clean",
        "_point_mode",
    )

    def __init__(
        self,
        stream: Any,
        x0: float,
        y0: float,
        x1: float,
        y1: float,
        visible: Callable[[float, float], bool],
        interpolate: Callable[
            [list[float] | None, list[float] | None, float, Any], None
        ],
        compare_intersection: Callable[[_Intersection, _Intersection], int],
    ) -> None:
        self.stream = stream
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.visible = visible
        self.interpolate = interpolate
        self.compare_intersection = compare_intersection
        self.active_stream = stream
        self.buffer_stream = clip_buffer()
        self.segments: list[Any] | None = None
        self.polygon: list[list[list[float]]] | None = None
        self.ring: list[list[float]] | None = None
        self.x__ = self.y__ = math.nan
        self.v__ = False
        self.x_ = self.y_ = math.nan
        self.v_ = False
        self.first = True
        self.clean = True
        self._point_mode = "visible"

    def point(self, x: float, y: float, z: Any = None) -> None:
        if self._point_mode == "visible":
            if self.visible(x, y):
                self.active_stream.point(x, y)
        else:
            self._line_point(x, y, z)

    def _polygon_inside(self) -> int:
        winding = 0
        assert self.polygon is not None
        for ring in self.polygon:
            m = len(ring)
            if m < 2:
                continue
            point = ring[0]
            b0, b1 = point[0], point[1]
            j = 1
            while j < m:
                a0, a1 = b0, b1
                point = ring[j]
                b0, b1 = point[0], point[1]
                if a1 <= self.y1:
                    if (
                        b1 > self.y1
                        and (b0 - a0) * (self.y1 - a1) > (b1 - a1) * (self.x0 - a0)
                    ):
                        winding += 1
                else:
                    if (
                        b1 <= self.y1
                        and (b0 - a0) * (self.y1 - a1) < (b1 - a1) * (self.x0 - a0)
                    ):
                        winding -= 1
                j += 1
        return winding

    def polygonStart(self) -> None:
        self.active_stream = self.buffer_stream
        self.segments = []
        self.polygon = []
        self.clean = True

    def polygonEnd(self) -> None:
        assert self.polygon is not None and self.segments is not None
        winding = self._polygon_inside()
        start_inside = winding
        clean_inside = self.clean and bool(winding)
        self.segments = merge(self.segments)
        vis = len(self.segments)
        if clean_inside or vis:
            self.stream.polygonStart()
            if clean_inside:
                self.stream.lineStart()
                self.interpolate(None, None, 1.0, self.stream)
                self.stream.lineEnd()
            if vis:
                clip_rejoin(
                    self.segments,
                    self.compare_intersection,
                    start_inside,
                    self.interpolate,
                    self.stream,
                )
            self.stream.polygonEnd()
        self.active_stream = self.stream
        self.segments = None
        self.polygon = None
        self.ring = None

    def lineStart(self) -> None:
        self._point_mode = "line"
        if self.polygon is not None:
            self.ring = []
            self.polygon.append(self.ring)
        self.first = True
        self.v_ = False
        self.x_ = self.y_ = math.nan

    def lineEnd(self) -> None:
        if self.segments is not None:
            self._line_point(self.x__, self.y__)
            if self.v__ and self.v_:
                self.buffer_stream.rejoin()
            self.segments.append(self.buffer_stream.result())
        self._point_mode = "visible"
        if self.v_:
            self.active_stream.lineEnd()

    def _point_visible(self, x: float, y: float, z: Any = None) -> None:
        if self.visible(x, y):
            self.active_stream.point(x, y)

    def _line_point(self, x: float, y: float, z: Any = None) -> None:
        v = self.visible(x, y)
        if self.polygon is not None and self.ring is not None:
            self.ring.append([x, y])
        if self.first:
            self.x__, self.y__, self.v__ = x, y, v
            self.first = False
            if v:
                self.active_stream.lineStart()
                self.active_stream.point(x, y)
        else:
            if v and self.v_:
                self.active_stream.point(x, y)
            else:
                cx = max(clip_min, min(clip_max, self.x_))
                cy = max(clip_min, min(clip_max, self.y_))
                bx = max(clip_min, min(clip_max, x))
                by = max(clip_min, min(clip_max, y))
                a = [cx, cy]
                b = [bx, by]
                if clip_line_rect(a, b, self.x0, self.y0, self.x1, self.y1):
                    if not self.v_:
                        self.active_stream.lineStart()
                        self.active_stream.point(a[0], a[1])
                    self.active_stream.point(b[0], b[1])
                    if not v:
                        self.active_stream.lineEnd()
                    self.clean = False
                elif v:
                    self.active_stream.lineStart()
                    self.active_stream.point(x, y)
                    self.clean = False
        self.x_, self.y_, self.v_ = x, y, v
