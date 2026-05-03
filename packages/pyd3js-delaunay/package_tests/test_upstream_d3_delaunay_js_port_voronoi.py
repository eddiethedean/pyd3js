"""Port of d3/d3-delaunay@v6.0.4 `test/voronoi-test.js` to pytest (pure Python)."""

from __future__ import annotations

from array import array

from pyd3js_delaunay import Delaunay


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


def test_voronoi_render_cell_noop_for_coincident_points() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 0]]).voronoi([-1, -1, 2, 2])
    assert v.render_cell(3, {}) is None


def test_voronoi_render_cell_midpoint_coincident_with_circumcenter() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [0, 1]]).voronoi([-1, -1, 2, 2])
    ctx = _Context()
    assert (v.render_cell(0, ctx), ctx.toString()) == (
        None,
        "M-1,-1L0.5,-1L0.5,0.5L-1,0.5Z",
    )
    assert (v.render_cell(1, ctx), ctx.toString()) == (
        None,
        "M2,-1L2,2L0.5,0.5L0.5,-1Z",
    )
    assert (v.render_cell(2, ctx), ctx.toString()) == (
        None,
        "M-1,2L-1,0.5L0.5,0.5L2,2Z",
    )


def test_voronoi_contains_false_for_coincident_points() -> None:
    v = Delaunay.from_points([[0, 0], [1, 0], [0, 1], [1, 0]]).voronoi([-1, -1, 2, 2])
    assert v.contains(3, 1, 0) is False
    assert v.contains(1, 1, 0) is True


def test_voronoi_update_updates_the_voronoi() -> None:
    d = Delaunay.from_points([[0, 0], [300, 0], [0, 300], [300, 300], [100, 100]])
    v = d.voronoi([-500, -500, 500, 500])
    for i in range(len(d.points)):
        d.points[i] = 10 - d.points[i]
    p = v.update().cell_polygon(1)
    assert p == [
        [-500, 500],
        [-500, -140],
        [-240, -140],
        [-140, 60],
        [-140, 500],
        [-500, 500],
    ]


def test_voronoi_update_updates_a_degenerate_voronoi() -> None:
    pts = [10, 10, -290, 10, 10, -290, -290, -290, -90, -90]
    d = Delaunay(array("d", [0.0] * len(pts)))
    v = d.voronoi([-500, -500, 500, 500])
    assert v.cell_polygon(0) == [
        [500, -500],
        [500, 500],
        [-500, 500],
        [-500, -500],
        [500, -500],
    ]
    assert v.cell_polygon(1) is None
    for i in range(len(d.points)):
        d.points[i] = pts[i]
    p = v.update().cell_polygon(1)
    assert p == [
        [-500, 500],
        [-500, -140],
        [-240, -140],
        [-140, 60],
        [-140, 500],
        [-500, 500],
    ]


def test_zero_length_edges_removed() -> None:
    v1 = Delaunay.from_points([[50, 10], [10, 50], [10, 10], [200, 100]]).voronoi(
        [40, 40, 440, 180]
    )
    assert v1.cell_polygon(0) is not None
    assert len(v1.cell_polygon(0) or []) == 4

    v2 = Delaunay.from_points([[10, 10], [20, 10]]).voronoi([0, 0, 30, 20])
    got = v2.cell_polygon(0)
    assert got is not None
    assert any(
        got == exp
        for exp in [
            [[0, 20], [0, 0], [15, 0], [15, 20], [0, 20]],
            [[15.0, 20.0], [0.0, 20.0], [0.0, 0.0], [15.0, 0.0], [15.0, 20.0]],
        ]
    )


def test_voronoi_neighbors_are_clipped() -> None:
    v = Delaunay.from_points(
        [[300, 10], [200, 100], [300, 100], [10, 10], [350, 200], [350, 400]]
    ).voronoi([0, 0, 500, 150])
    got = [sorted(list(v.neighbors(i))) for i in range(6)]
    assert got == [[1, 2], [0, 2, 3], [0, 1, 4], [1], [2], []]


def test_unnecessary_corner_points_avoided_88() -> None:
    cases: list[tuple[list[list[float]], list[int]]] = [
        ([[289, 25], [3, 22], [93, 165], [282, 184], [65, 89]], [6, 4, 6, 5, 6]),
        ([[189, 13], [197, 26], [47, 133], [125, 77], [288, 15]], [4, 6, 5, 6, 5]),
        ([[44, 42], [210, 193], [113, 103], [185, 43], [184, 37]], [5, 5, 7, 5, 6]),
    ]
    for points, lengths in cases:
        v = Delaunay.from_points(points).voronoi([0, 0, 290, 190])
        got = [len(p) for p in v.cell_polygons()]
        assert got == lengths


def test_degenerate_triangle_avoided() -> None:
    pts = [
        [424.75, 253.75],
        [424.75, 253.74999999999997],
        [407.17640687119285, 296.17640687119285],
        [364.75, 313.75],
        [322.32359312880715, 296.17640687119285],
        [304.75, 253.75],
        [322.32359312880715, 211.32359312880715],
        [364.75, 193.75],
        [407.17640687119285, 211.32359312880715],
        [624.75, 253.75],
        [607.1764068711929, 296.17640687119285],
        [564.75, 313.75],
        [522.3235931288071, 296.17640687119285],
        [504.75, 253.75],
        [564.75, 193.75],
    ]
    v = Delaunay.from_points(pts).voronoi([10, 10, 960, 500])
    assert v.cell_polygon(0) is not None
    assert len(v.cell_polygon(0) or []) == 4


def test_cell_polygons_filter_empty_and_have_index_property() -> None:
    pts = [[0, 0], [3, 3], [1, 1], [-3, -2]]
    v = Delaunay.from_points(pts).voronoi([0, 0, 2, 2])
    cells = list(v.cell_polygons())
    # Upstream yields only non-empty cells; Python yields CellPolygon (list subclass) with `.index`.
    assert [c.index for c in cells] == [0, 2]
    assert list(cells[0]) == [[0, 0], [1, 0], [0, 1], [0, 0]]
    assert list(cells[1]) == [[2, 2], [0, 2], [0, 1], [1, 0], [2, 0], [2, 2]]


def test_voronoi_neighbors_correct() -> None:
    points = [[10, 10], [36, 27], [90, 19], [50, 75]]
    v = Delaunay.from_points(points).voronoi([0, 0, 100, 90])
    got = [sorted(list(v.neighbors(i))) for i in range(4)]
    assert got == [[1], [0, 2, 3], [1, 3], [1, 2]]


def test_voronoi_neighbors_correct_flipped_vertically() -> None:
    points = [[10, -10], [36, -27], [90, -19], [50, -75]]
    v = Delaunay.from_points(points).voronoi([0, -90, 100, 0])
    got = [sorted(list(v.neighbors(i))) for i in range(4)]
    assert got == [[1], [0, 2, 3], [1, 3], [1, 2]]


def test_voronoi_neighbors_correct_flipped_horizontally() -> None:
    points = [[-10, 10], [-36, 27], [-90, 19], [-50, 75]]
    v = Delaunay.from_points(points).voronoi([-100, 0, 0, 90])
    got = [sorted(list(v.neighbors(i))) for i in range(4)]
    assert got == [[1], [0, 2, 3], [1, 3], [1, 2]]


def test_voronoi_neighbors_correct_rotated() -> None:
    points = [[-10, -10], [-36, -27], [-90, -19], [-50, -75]]
    v = Delaunay.from_points(points).voronoi([-100, -90, 0, 0])
    got = [sorted(list(v.neighbors(i))) for i in range(4)]
    assert got == [[1], [0, 2, 3], [1, 3], [1, 2]]


def test_voronoi_expected_result_136() -> None:
    points = [
        [447.27981036477433, 698.9400262172304],
        [485.27830313288746, 668.9946483670656],
        [611.9525697080425, 397.71056371206487],
        [491.44637766366105, 692.071157339428],
        [697.553622336339, 692.071157339428],
        [497.00778156318086, 667.1990851383492],
        [691.9922184368191, 667.1990851383492],
        [544.9897579870977, 407.0828550310619],
        [543.1738215956482, 437.35879519252677],
    ]
    v = Delaunay.from_points(points).voronoi([0, 0, 1000, 1000])
    assert v.cell_polygon(3) is not None
    assert len(v.cell_polygon(3) or []) == 6


def test_voronoi_expected_result_141() -> None:
    points: list[list[float]] = [[10, 190]] + [[i * 80, (i * 50) / 7] for i in range(7)]
    v = Delaunay.from_points(points).voronoi([1, 1, 499, 199])
    got = [len(p) for p in v.cell_polygons()]
    assert got == [7, 5, 5, 5, 6, 5, 5, 5]
