"""Composite Albers USA projection (d3-geo `projection/albersUsa.js`)."""

from __future__ import annotations

from typing import Any

epsilon = 1e-6
_MISSING = object()


class _MultiplexStream:
    __slots__ = ("streams",)

    def __init__(self, streams: list[Any]) -> None:
        self.streams = streams

    def point(self, x: float, y: float, z: Any = None) -> None:
        for s in self.streams:
            if z is not None:
                s.point(x, y, z)
            else:
                s.point(x, y)

    def sphere(self) -> None:
        for s in self.streams:
            getattr(s, "sphere", lambda: None)()

    def lineStart(self) -> None:
        for s in self.streams:
            s.lineStart()

    def lineEnd(self) -> None:
        for s in self.streams:
            s.lineEnd()

    def polygonStart(self) -> None:
        for s in self.streams:
            s.polygonStart()

    def polygonEnd(self) -> None:
        for s in self.streams:
            s.polygonEnd()


class _PointCapture:
    __slots__ = ("_cell",)

    def __init__(self, cell: list[Any]) -> None:
        self._cell = cell

    def point(self, x: float, y: float, z: Any = None) -> None:
        self._cell[0] = [x, y]


def geo_albers_usa() -> Any:
    from pyd3js_geo._core import (
        fitExtent,
        fitHeight,
        fitSize,
        fitWidth,
        geoAlbers,
        geoConicEqualArea,
    )

    cache: Any = None
    cache_stream: Any = None
    lower48 = geoAlbers()
    alaska = geoConicEqualArea().rotate([154, 0]).center([-2, 58.5]).parallels([55, 65])
    hawaii = geoConicEqualArea().rotate([157, 0]).center([-3, 19.9]).parallels([8, 18])

    lower48_point: Any = None
    alaska_point: Any = None
    hawaii_point: Any = None
    point_cell: list[Any] = [None]
    point_stream = _PointCapture(point_cell)

    def reset() -> Any:
        nonlocal cache, cache_stream
        cache = cache_stream = None
        return albers_usa

    def albers_usa(coords: list[float]) -> list[float] | None:
        x, y = coords[0], coords[1]
        point_cell[0] = None
        lower48_point.point(x, y)
        if point_cell[0] is not None:
            return point_cell[0]  # pragma: no cover
        alaska_point.point(x, y)
        if point_cell[0] is not None:
            return point_cell[0]  # pragma: no cover
        hawaii_point.point(x, y)
        return point_cell[0]

    def invert(coords: list[float]) -> list[float] | None:
        k = lower48.scale()
        t = lower48.translate()
        x = (coords[0] - t[0]) / k
        y = (coords[1] - t[1]) / k
        if y >= 0.120 and y < 0.234 and x >= -0.425 and x < -0.214:
            return alaska.invert(coords)  # pragma: no cover
        if y >= 0.166 and y < 0.234 and x >= -0.214 and x < -0.115:
            return hawaii.invert(coords)  # pragma: no cover
        return lower48.invert(coords)

    albers_usa.invert = invert  # type: ignore[attr-defined]

    def _apply_region_clips(x: float, y: float, k: float) -> None:
        """Set lower48 / Alaska / Hawaii clip extents from translate (x,y) and scale k."""
        nonlocal lower48_point, alaska_point, hawaii_point
        lower48_point = (
            lower48.translate([x, y])
            .clipExtent(
                [
                    [x - 0.455 * k, y - 0.238 * k],
                    [x + 0.455 * k, y + 0.238 * k],
                ]
            )
            .stream(point_stream)
        )

        alaska_point = (
            alaska.translate([x - 0.307 * k, y + 0.201 * k])
            .clipExtent(
                [
                    [x - 0.425 * k + epsilon, y + 0.120 * k + epsilon],
                    [x - 0.214 * k - epsilon, y + 0.234 * k - epsilon],
                ]
            )
            .stream(point_stream)
        )

        hawaii_point = (
            hawaii.translate([x - 0.205 * k, y + 0.212 * k])
            .clipExtent(
                [
                    [x - 0.214 * k + epsilon, y + 0.166 * k + epsilon],
                    [x - 0.115 * k - epsilon, y + 0.234 * k - epsilon],
                ]
            )
            .stream(point_stream)
        )

    def stream(sink: Any) -> Any:
        nonlocal cache, cache_stream
        if cache is not None and cache_stream is sink:
            return cache
        cache_stream = sink
        cache = _MultiplexStream(
            [
                lower48.stream(cache_stream),
                alaska.stream(sink),
                hawaii.stream(sink),
            ]
        )
        return cache

    albers_usa.stream = stream  # type: ignore[attr-defined]

    def precision(v: Any = _MISSING) -> Any:
        if v is _MISSING:
            return lower48.precision()
        lower48.precision(v)
        alaska.precision(v)
        hawaii.precision(v)
        return reset()

    albers_usa.precision = precision  # type: ignore[attr-defined]

    def scale(v: Any = _MISSING) -> Any:
        if v is _MISSING:
            return lower48.scale()
        lower48.scale(v)
        alaska.scale(v * 0.35)
        hawaii.scale(v)
        return albers_usa.translate(lower48.translate())

    albers_usa.scale = scale  # type: ignore[attr-defined]

    def translate(v: Any = _MISSING) -> Any:
        if v is _MISSING:
            return lower48.translate()
        k = lower48.scale()
        x, y = float(v[0]), float(v[1])
        lower48.translate([x, y])
        _apply_region_clips(x, y, k)

        return reset()

    albers_usa.translate = translate  # type: ignore[attr-defined]

    albers_usa.fitExtent = lambda extent, obj: fitExtent(albers_usa, extent, obj)  # type: ignore[attr-defined]
    albers_usa.fitSize = lambda size, obj: fitSize(albers_usa, size, obj)  # type: ignore[attr-defined]
    albers_usa.fitWidth = lambda width, obj: fitWidth(albers_usa, width, obj)  # type: ignore[attr-defined]
    albers_usa.fitHeight = lambda height, obj: fitHeight(albers_usa, height, obj)  # type: ignore[attr-defined]

    albers_usa.scale(1070)
    return albers_usa
