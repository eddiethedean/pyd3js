"""Always-on smoke tests (not gated by PYD3JS_GEO_FULL_UPSTREAM)."""

from __future__ import annotations

import math

from pyd3js_geo import (
    geoDistance,
    geoInterpolate,
    geoMercator,
    geoPath,
    geoRotation,
    geoStream,
)

from test_support import assert_in_delta


def test_geo_distance_quarter_equator() -> None:
    assert abs(geoDistance([0, 0], [90, 0]) - math.pi / 2) <= 1e-10


def test_geo_interpolate_midpoint() -> None:
    f = geoInterpolate([0, 0], [90, 0])
    assert abs(f.distance - math.pi / 2) <= 1e-10
    assert_in_delta(f(0.5), [45, 0])


def test_geo_rotation_forward_and_invert() -> None:
    rotate = geoRotation([90, 0])
    assert_in_delta(rotate([0, 0]), [90, 0])
    assert_in_delta(rotate.invert([90, 0]), [0, 0])


def test_geo_stream_point_optional_z() -> None:
    events: list[tuple] = []

    class Stream:
        def point(self, x, y, z=None):
            events.append(("point", x, y, z))

        def sphere(self):
            events.append(("sphere",))

        def lineStart(self):
            events.append(("lineStart",))

        def lineEnd(self):
            events.append(("lineEnd",))

        def polygonStart(self):
            events.append(("polygonStart",))

        def polygonEnd(self):
            events.append(("polygonEnd",))

    geoStream({"type": "Point", "coordinates": [1, 2]}, Stream())
    assert events == [("point", 1, 2, None)]


def test_geo_mercator_center_translate() -> None:
    projection = geoMercator().center([10, 20]).translate([200, 100])
    assert_in_delta(projection([10, 20]), [200, 100])


def test_geo_path_mercator_small_linestring() -> None:
    projection = geoMercator().translate([0, 0]).scale(1)
    path = geoPath(projection)
    line = {"type": "LineString", "coordinates": [[0, 0], [1, 0]]}
    assert path(line) == "M0,0L0.017,0"
