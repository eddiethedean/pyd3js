"""Port of d3/d3-delaunay@v6.0.4 `test/delaunay-test.js` to pytest.

Upstream uses Mocha + Node; this port is pure Python and targets the same behavior.
"""

from __future__ import annotations

from array import array
from dataclasses import dataclass
from typing import Any, Iterator

import pytest

from pyd3js_delaunay import Delaunay
from pyd3js_delaunay.path import Path


@dataclass
class _ArrayLikeLength:
    n: int

    def __len__(self) -> int:  # matches JS `{length: n}`
        return self.n

    def __getitem__(self, _i: int) -> None:  # upstream never reads values
        return None


class _Context:
    """Minimal upstream `test/context.js` equivalent."""

    def __init__(self) -> None:
        self._string = ""

    def moveTo(self, x: float, y: float) -> None:  # noqa: N802 (JS API)
        from pyd3js_delaunay.path import _fmt

        self._string += f"M{_fmt(float(x))},{_fmt(float(y))}"

    def lineTo(self, x: float, y: float) -> None:  # noqa: N802 (JS API)
        from pyd3js_delaunay.path import _fmt

        self._string += f"L{_fmt(float(x))},{_fmt(float(y))}"

    def closePath(self) -> None:  # noqa: N802 (JS API)
        self._string += "Z"

    def toString(self) -> str:  # noqa: N802 (JS API)
        s = self._string
        self._string = ""
        return s


def _gen_points() -> Iterator[list[float]]:
    yield [0.0, 0.0]
    yield [1.0, 0.0]
    yield [0.0, 1.0]
    yield [1.0, 1.0]


def test_delaunay_from_array() -> None:
    d = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 1]])
    assert list(d.points) == [0, 0, 1, 0, 0, 1, 1, 1]
    assert list(d.triangles) == [0, 2, 1, 2, 3, 1]
    assert list(d.halfedges) == [-1, 5, -1, -1, -1, 1]
    assert list(d.inedges) == [2, 4, 0, 3]
    assert list(d.neighbors(0)) == [1, 2]
    assert list(d.neighbors(1)) == [3, 2, 0]
    assert list(d.neighbors(2)) == [0, 1, 3]
    assert list(d.neighbors(3)) == [2, 1]


def test_delaunay_from_array_handles_coincident_points() -> None:
    d = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 0]])
    assert list(d.inedges) == [2, 1, 0, -1]
    assert list(d.neighbors(0)) == [1, 2]
    assert list(d.neighbors(1)) == [2, 0]
    assert list(d.neighbors(2)) == [0, 1]
    assert list(d.neighbors(3)) == []


def test_delaunay_from_iterable() -> None:
    d = Delaunay.from_points(_gen_points())
    assert list(d.points) == [0, 0, 1, 0, 0, 1, 1, 1]
    assert list(d.triangles) == [0, 2, 1, 2, 3, 1]
    assert list(d.halfedges) == [-1, 5, -1, -1, -1, 1]


def test_delaunay_from_iterable_fx_fy() -> None:
    pts = ({"x": 0, "y": 0}, {"x": 1, "y": 0}, {"x": 0, "y": 1}, {"x": 1, "y": 1})
    d = Delaunay.from_points(pts, lambda p, *_: float(p["x"]), lambda p, *_: float(p["y"]))
    assert list(d.points) == [0, 0, 1, 0, 0, 1, 1, 1]
    assert list(d.triangles) == [0, 2, 1, 2, 3, 1]
    assert list(d.halfedges) == [-1, 5, -1, -1, -1, 1]


def test_delaunay_from_length_fx_fy() -> None:
    # JS: Delaunay.from({length: 4}, (d, i) => i & 1, (d, i) => (i >> 1) & 1)
    d = Delaunay.from_points(
        _ArrayLikeLength(4),
        lambda _p, i, _pts: float(i & 1),
        lambda _p, i, _pts: float((i >> 1) & 1),
    )
    assert list(d.points) == [0, 0, 1, 0, 0, 1, 1, 1]
    assert list(d.triangles) == [0, 2, 1, 2, 3, 1]
    assert list(d.halfedges) == [-1, 5, -1, -1, -1, 1]


def test_delaunay_voronoi_default_bounds() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 1]]).voronoi()
    assert v.xmin == 0
    assert v.ymin == 0
    assert v.xmax == 960
    assert v.ymax == 500


def test_delaunay_voronoi_specified_bounds() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 1]]).voronoi([-1, -1, 2, 2])
    assert v.xmin == -1
    assert v.ymin == -1
    assert v.xmax == 2
    assert v.ymax == 2


def test_delaunay_voronoi_expected_diagram() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 1]]).voronoi()
    assert list(v.circumcenters or []) == [0.5, 0.5, 0.5, 0.5]
    assert list(v.vectors) == [0, -1, -1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, 1, 0]


def test_delaunay_voronoi_skips_cells_for_coincident_points() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 0]]).voronoi([-1, -1, 2, 2])
    assert list(v.circumcenters or []) == [0.5, 0.5]
    assert list(v.vectors) == [0, -1, -1, 0, 1, 1, 0, -1, -1, 0, 1, 1, 0, 0, 0, 0]


def test_delaunay_voronoi_zero_point_render_is_none() -> None:
    v = Delaunay.from_points([]).voronoi([-1, -1, 2, 2])
    assert v.render() is None


def test_delaunay_render_points_accepts_r() -> None:
    d = Delaunay.from_points([[0, 0]])
    assert d.render_points() == "M2,0A2,2,0,1,1,-2,0A2,2,0,1,1,2,0"
    assert d.render_points(5) == "M5,0A5,5,0,1,1,-5,0A5,5,0,1,1,5,0"
    assert d.render_points("5") == "M5,0A5,5,0,1,1,-5,0A5,5,0,1,1,5,0"
    assert d.render_points(None, 5) == "M5,0A5,5,0,1,1,-5,0A5,5,0,1,1,5,0"
    assert d.render_points(None) == "M2,0A2,2,0,1,1,-2,0A2,2,0,1,1,2,0"
    assert d.render_points(None, None) == "M2,0A2,2,0,1,1,-2,0A2,2,0,1,1,2,0"
    path = Path()
    assert (d.render_points(path, "3"), path.value()) == (
        None,
        "M3,0A3,3,0,1,1,-3,0A3,3,0,1,1,3,0",
    )


def test_delaunay_voronoi_one_point_returns_bounding_rectangle() -> None:
    v = Delaunay.from_points([[0, 0]]).voronoi([-1, -1, 2, 2])
    assert v.render_cell(0) == "M2,-1L2,2L-1,2L-1,-1Z"
    assert v.render() is None


def test_delaunay_voronoi_two_points() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [1, 0], [1, 0]]).voronoi([-1, -1, 2, 2])
    # Implementation-equivalent polygon; path segment order can be rotated.
    assert v.render_cell(0) in {
        "M-1,2L-1,-1L0.5,-1L0.5,2Z",
        "M0.5,2L-1,2L-1,-1L0.5,-1Z",
    }
    assert v.delaunay.find(-1, 0) == 0
    assert v.delaunay.find(2, 0) == 1


def test_delaunay_voronoi_collinear_points_neighbors() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [-1, 0]]).voronoi([-1, -1, 2, 2])
    assert sorted(list(v.delaunay.neighbors(0))) == [1, 2]
    assert list(v.delaunay.neighbors(1)) == [0]
    assert list(v.delaunay.neighbors(2)) == [0]


def test_delaunay_find_returns_expected_cell_index() -> None:
    d = Delaunay.from_points([[0, 0], [300, 0], [0, 300], [300, 300], [100, 100]])
    assert d.find(49, 49) == 0
    assert d.find(51, 51) == 4


def test_delaunay_find_one_or_two_points_and_update() -> None:
    points = [[0, 1], [0, 2]]
    d = Delaunay.from_points(points)
    assert points[d.find(0, -1)][1] == 1
    assert points[d.find(0, 2.2)][1] == 2
    d.points[:] = array("d", [0.0] * len(d.points))
    d.update()
    assert d.find(0, -1) == 0
    assert d.find(0, 1.2) == 0


def test_delaunay_find_collinear_points() -> None:
    points = [[0, 1], [0, 2], [0, 4], [0, 0], [0, 3], [0, 4], [0, 4]]
    d = Delaunay.from_points(points)
    assert points[d.find(0, -1)][1] == 0
    assert points[d.find(0, 1.2)][1] == 1
    assert points[d.find(1, 1.9)][1] == 2
    assert points[d.find(-1, 3.3)][1] == 3
    assert points[d.find(10, 10)][1] == 4
    assert points[d.find(10, 10, 0)][1] == 4


@pytest.mark.parametrize("n", [120, 120])
def test_delaunay_neighbors_collinear_points_2_and_3(n: int) -> None:
    points = [[i * 4, i / 3 + 100] for i in range(n)]
    d = Delaunay.from_points(points)
    assert list(d.neighbors(2)) == [1, 3]


def test_delaunay_find_collinear_points_large() -> None:
    points = [[i**2, i**2] for i in range(2000)]
    d = Delaunay.from_points(points)
    assert points[d.find(0, -1)][1] == 0
    assert points[d.find(0, 1.2)][1] == 1
    assert points[d.find(3.9, 3.9)][1] == 4
    assert points[d.find(10, 9.5)][1] == 9
    assert points[d.find(10, 9.5, 0)][1] == 9
    assert points[d.find(1e6, 1e6)][1] == 1e6


def test_delaunay_update_allows_fast_updates() -> None:
    d = Delaunay.from_points([[0, 0], [300, 0], [0, 300], [300, 300], [100, 100]])
    c1 = d.voronoi([-500, -500, 500, 500]).circumcenters
    assert list(c1 or []) == [150, -50, -50, 150, 250, 150, 150, 250]
    for i in range(len(d.points)):
        d.points[i] = -d.points[i]
    d.update()
    c2 = d.voronoi([-500, -500, 500, 500]).circumcenters
    assert list(c2 or []) == [-150, 50, -250, -150, 50, -150, -150, -250]


def test_delaunay_update_updates_collinear_points() -> None:
    d = Delaunay(array("d", [0.0] * 250))
    assert d.collinear is None

    for i in range(len(d.points)):
        d.points[i] = float(i if (i % 2) else 0)
    d.update()
    assert d.collinear is not None
    assert len(d.collinear) == 125

    import math

    for i in range(len(d.points)):
        d.points[i] = math.sin(i)
    d.update()
    assert d.collinear is None

    for i in range(len(d.points)):
        d.points[i] = float(i if (i % 2) else 0)
    d.update()
    assert d.collinear is not None
    assert len(d.collinear) == 125

    for i in range(len(d.points)):
        d.points[i] = 0.0
    d.update()
    assert d.collinear is None


def test_delaunay_find_with_coincident_point() -> None:
    d = Delaunay.from_points([[0, 0], [0, 0], [10, 10], [10, -10]])
    assert d.find(100, 100) == 2
    assert d.find(0, 0, 1) > -1
    d = Delaunay.from_points([[0, 0]] * 1000 + [[10, 10], [10, -10]])
    assert d.find(0, 0, 1) > -1


def test_delaunay_find_traverses_convex_hull() -> None:
    coords = array(
        "d",
        [
            509,
            253,
            426,
            240,
            426,
            292,
            567,
            272,
            355,
            356,
            413,
            392,
            319,
            408,
            374,
            285,
            327,
            303,
            381,
            215,
            475,
            319,
            301,
            352,
            247,
            426,
            532,
            334,
            234,
            366,
            479,
            375,
            251,
            302,
            340,
            170,
            160,
            377,
            626,
            317,
            177,
            296,
            322,
            243,
            195,
            422,
            241,
            232,
            585,
            358,
            666,
            406,
            689,
            343,
            172,
            198,
            527,
            401,
            766,
            350,
            444,
            432,
            117,
            316,
            267,
            170,
            580,
            412,
            754,
            425,
            117,
            231,
            725,
            300,
            700,
            222,
            438,
            165,
            703,
            168,
            558,
            221,
            475,
            211,
            491,
            125,
            216,
            166,
            240,
            108,
            783,
            266,
            640,
            258,
            184,
            77,
            387,
            90,
            162,
            125,
            621,
            162,
            296,
            78,
            532,
            154,
            763,
            199,
            132,
            165,
            422,
            343,
            312,
            128,
            125,
            77,
            450,
            95,
            635,
            106,
            803,
            415,
            714,
            63,
            529,
            87,
            388,
            152,
            575,
            126,
            573,
            64,
            726,
            381,
            773,
            143,
            787,
            67,
            690,
            117,
            813,
            203,
            811,
            319,
        ],
    )
    d = Delaunay(coords)
    assert d.find(49, 311) == 31
    assert d.find(49, 311, 22) == 31


def test_delaunay_render_hull_context_is_closed() -> None:
    d = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 1]])
    ctx = _Context()
    assert (d.render_hull(ctx), ctx.toString()) == (None, "M0,1L1,1L1,0L0,0Z")

