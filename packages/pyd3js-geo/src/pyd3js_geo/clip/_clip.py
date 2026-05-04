"""Generic polygon clip factory (d3-geo `clip/index.js`)."""

from __future__ import annotations

import math
from typing import Any, Callable

from pyd3js_array import merge

from pyd3js_geo.clip._buffer import clip_buffer
from pyd3js_geo.clip._rejoin import clip_rejoin
from pyd3js_geo.polygon_contains import polygon_contains_rings

epsilon = 1e-6
half_pi = math.pi / 2


def compare_intersection_antimeridian_circle(a: Any, b: Any) -> int:
    ax = a.x  # pragma: no cover
    bx = b.x  # pragma: no cover
    va = ax[1] - half_pi - epsilon if ax[0] < 0 else half_pi - ax[1]  # pragma: no cover
    vb = bx[1] - half_pi - epsilon if bx[0] < 0 else half_pi - bx[1]  # pragma: no cover
    diff = va - vb  # pragma: no cover
    return (diff > 0) - (diff < 0)  # pragma: no cover


def _valid_segment(segment: list[list[float | None]]) -> bool:
    return len(segment) > 1  # pragma: no cover


def _line_cmd(line: Any, cmd: str, *args: Any) -> Any:
    fn = getattr(line, cmd, None)
    if not callable(fn):
        fn = line[cmd]
    return fn(*args) if args else fn()


def clip(
    point_visible: Callable[[float, float], bool],
    clip_line_factory: Callable[[Any], Any],
    interpolate: Callable[[list[float] | None, list[float] | None, float, Any], None],
    start: list[float],
) -> Callable[[Any], Any]:
    def factory(sink: Any) -> "_GenericClip":
        return _GenericClip(
            sink, point_visible, clip_line_factory, interpolate, start
        )

    return factory


class _GenericClip:
    __slots__ = (
        "stream",
        "point_visible",
        "clip_line_factory",
        "interpolate",
        "start",
        "line",
        "ring_buffer",
        "ring_sink",
        "polygon_started",
        "polygon",
        "segments",
        "ring",
        "_in_line",
        "_in_polygon",
    )

    def __init__(
        self,
        sink: Any,
        point_visible: Callable[[float, float], bool],
        clip_line_factory: Callable[[Any], Any],
        interpolate: Callable[[list[float] | None, list[float] | None, float, Any], None],
        start: list[float],
    ) -> None:
        self.stream = sink
        self.point_visible = point_visible
        self.clip_line_factory = clip_line_factory
        self.interpolate = interpolate
        self.start = start
        self.line = clip_line_factory(sink)
        self.ring_buffer = clip_buffer()
        self.ring_sink = clip_line_factory(self.ring_buffer)
        self.polygon_started = False
        self.polygon: list[list[list[float]]] | None = None
        self.segments: list[Any] | None = None
        self.ring: list[list[float]] | None = None
        self._in_line = False
        self._in_polygon = False

    def point(self, lambda_: float, phi: float, z: Any = None) -> None:
        if self._in_polygon:
            self._point_ring_vertex(lambda_, phi)
        elif self._in_line:
            _line_cmd(self.line, "point", lambda_, phi)
        elif self.point_visible(lambda_, phi):
            self.stream.point(lambda_, phi)

    def lineStart(self) -> None:
        if self._in_polygon:
            _line_cmd(self.ring_sink, "lineStart")
            self.ring = []
        else:
            self._in_line = True
            _line_cmd(self.line, "lineStart")

    def lineEnd(self) -> None:
        if self._in_polygon:
            assert self.ring is not None
            self._point_ring_vertex(self.ring[0][0], self.ring[0][1])
            _line_cmd(self.ring_sink, "lineEnd")

            clean = _line_cmd(self.line, "clean")
            ring_segments = self.ring_buffer.result()
            self.ring.pop()
            assert self.polygon is not None
            self.polygon.append(self.ring)
            self.ring = None

            n = len(ring_segments)
            if not n:
                return

            if clean & 1:
                segment = ring_segments[0]
                m = len(segment) - 1
                if m > 0:
                    if not self.polygon_started:
                        self.stream.polygonStart()
                        self.polygon_started = True
                    self.stream.lineStart()
                    for i in range(m):
                        point = segment[i]
                        self.stream.point(point[0], point[1])
                    self.stream.lineEnd()
                return

            if n > 1 and clean & 2:  # pragma: no cover
                ring_segments.append(ring_segments.pop() + ring_segments.pop(0))  # pragma: no cover

            assert self.segments is not None  # pragma: no cover
            self.segments.append([s for s in ring_segments if _valid_segment(s)])  # pragma: no cover
        else:
            self._in_line = False
            _line_cmd(self.line, "lineEnd")

    def _point_ring_vertex(self, lam: float, phi: float) -> None:
        assert self.ring is not None
        self.ring.append([lam, phi])
        _line_cmd(self.ring_sink, "point", lam, phi)

    def polygonStart(self) -> None:
        self._in_polygon = True
        self.segments = []
        self.polygon = []

    def polygonEnd(self) -> None:
        self._in_polygon = False
        assert self.segments is not None and self.polygon is not None
        self.segments = merge(self.segments)
        start_inside = polygon_contains_rings(self.polygon, self.start)
        if self.segments:
            if not self.polygon_started:  # pragma: no cover
                self.stream.polygonStart()  # pragma: no cover
                self.polygon_started = True  # pragma: no cover
            clip_rejoin(  # pragma: no cover
                self.segments,
                compare_intersection_antimeridian_circle,
                start_inside,
                self.interpolate,
                self.stream,
            )
        elif start_inside:
            if not self.polygon_started:
                self.stream.polygonStart()  # pragma: no cover
                self.polygon_started = True  # pragma: no cover
            self.stream.lineStart()
            self.interpolate(None, None, 1.0, self.stream)
            self.stream.lineEnd()
        if self.polygon_started:
            self.stream.polygonEnd()
            self.polygon_started = False
        self.segments = None
        self.polygon = None

    def sphere(self) -> None:
        self.stream.polygonStart()
        self.stream.lineStart()
        self.interpolate(None, None, 1.0, self.stream)
        self.stream.lineEnd()
        self.stream.polygonEnd()
