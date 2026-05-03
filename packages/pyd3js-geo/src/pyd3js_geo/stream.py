"""GeoJSON stream dispatch (d3-geo `stream.js`) and stream transforms (`transform.js`)."""

from __future__ import annotations

from typing import Any, Callable

from pyd3js_geo.math import radians
from pyd3js_geo.noop import noop


def geoStream(obj: Any, stream: Any) -> None:
    if not obj:
        return
    typ = obj.get("type")
    if typ == "Feature":
        geoStream(obj.get("geometry"), stream)
    elif typ == "FeatureCollection":
        for feature in obj.get("features", []):
            geoStream(feature.get("geometry"), stream)
    elif typ == "GeometryCollection":
        for geometry in obj.get("geometries", []):
            geoStream(geometry, stream)
    elif typ == "Sphere":
        stream.sphere()
    elif typ == "Point":
        c = obj.get("coordinates", [])
        stream.point(c[0], c[1], c[2] if len(c) > 2 else None)
    elif typ == "MultiPoint":
        for c in obj.get("coordinates", []):
            stream.point(c[0], c[1], c[2] if len(c) > 2 else None)
    elif typ == "LineString":
        _stream_line(obj.get("coordinates", []), stream, 0)
    elif typ == "MultiLineString":
        for line in obj.get("coordinates", []):
            _stream_line(line, stream, 0)
    elif typ == "Polygon":
        _stream_polygon(obj.get("coordinates", []), stream)
    elif typ == "MultiPolygon":
        for polygon in obj.get("coordinates", []):
            _stream_polygon(polygon, stream)


def _stream_line(coordinates: list[Any], stream: Any, closed: int) -> None:
    stream.lineStart()
    n = len(coordinates) - closed
    for c in coordinates[:n]:
        stream.point(c[0], c[1], c[2] if len(c) > 2 else None)
    stream.lineEnd()


def _stream_polygon(coordinates: list[Any], stream: Any) -> None:
    stream.polygonStart()
    for ring in coordinates:
        _stream_line(ring, stream, 1)
    stream.polygonEnd()


class TransformStream:
    def __init__(self, stream: Any, methods: dict[str, Callable[..., Any]]):
        self.stream = stream
        self._methods = methods

    def point(self, x: float, y: float, z: Any = None) -> None:
        f = self._methods.get("point")
        if f:
            return f(self, x, y, z) if z is not None else f(self, x, y)
        return self.stream.point(x, y) if z is None else self.stream.point(x, y, z)

    def sphere(self) -> None:
        return self._methods.get(
            "sphere", lambda s: getattr(s.stream, "sphere", noop)()
        )(self)

    def lineStart(self) -> None:
        return self._methods.get("lineStart", lambda s: s.stream.lineStart())(self)

    def lineEnd(self) -> None:
        return self._methods.get("lineEnd", lambda s: s.stream.lineEnd())(self)

    def polygonStart(self) -> None:
        return self._methods.get("polygonStart", lambda s: s.stream.polygonStart())(
            self
        )

    def polygonEnd(self) -> None:
        return self._methods.get("polygonEnd", lambda s: s.stream.polygonEnd())(self)


def transformer(
    methods: dict[str, Callable[..., Any]],
) -> Callable[[Any], TransformStream]:
    return lambda stream: TransformStream(stream, methods)


def _transform_radians_factory() -> Callable[[Any], Any]:
    return transformer(
        {
            "point": lambda s, x, y, z=None: (
                s.stream.point(x * radians, y * radians, z)
                if z is not None
                else s.stream.point(x * radians, y * radians)
            ),
        }
    )


def _transform_rotate_factory(
    rotate: Callable[[float, float], list[float]],
) -> Callable[[Any], Any]:
    def point_fn(s: Any, x: float, y: float, z: Any = None) -> Any:
        r = rotate(x, y)
        return (
            s.stream.point(r[0], r[1], z)
            if z is not None
            else s.stream.point(r[0], r[1])
        )

    return transformer({"point": point_fn})
