"""Deterministic canvas-style checks (d3-geo PNG snapshot tests are not run in Python).

Upstream compares rasterized output; here we assert the same `PathContext` command
sequence d3's path tests use (`test/path/test-context.js` style).
"""

from pyd3js_geo import geoIdentity, geoPath

from test_support import make_test_context


def test_geo_path_context_stream_matches_rounded_canvas_commands():
    ctx = make_test_context()
    path = geoPath(geoIdentity().translate([0, 0]).scale(1), ctx)
    path({"type": "LineString", "coordinates": [[0, 0], [10, 10]]})
    assert ctx.result() == [
        {"type": "moveTo", "x": 0, "y": 0},
        {"type": "lineTo", "x": 10, "y": 10},
    ]


def test_geo_path_context_point_geometry_emits_arc_commands():
    ctx = make_test_context()
    path = geoPath(geoIdentity().translate([0, 0]).scale(1), ctx)
    path.pointRadius(4)
    path({"type": "Point", "coordinates": [0, 0]})
    assert ctx.result() == [
        {"type": "moveTo", "x": 4, "y": 0},
        {"type": "arc", "x": 0, "y": 0, "r": 4},
    ]
