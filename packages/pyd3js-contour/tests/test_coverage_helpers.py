"""Branch coverage for helpers and density/contours accessors."""

from __future__ import annotations

import math
from unittest.mock import patch

import pytest

from pyd3js_contour._area import area
from pyd3js_contour._ascending import ascending
from pyd3js_contour._constant import constant
from pyd3js_contour._contains import contains
from pyd3js_contour._contains import _ring_contains
from pyd3js_contour._noop import noop
from pyd3js_contour._noop import noop_factory
from pyd3js_contour.contours import _above
from pyd3js_contour.contours import _finite
from pyd3js_contour.contours import _smooth1
from pyd3js_contour.contours import _valid
from pyd3js_contour.contours import contours
from pyd3js_contour.density import contourDensity


def test_constant_and_noop() -> None:
    f = constant(3)
    assert f() == 3
    assert noop() is None
    assert noop_factory()() is None


def test_ascending() -> None:
    assert ascending(2.0, 5.0) == -3.0


def test_area_triangle() -> None:
    ring = [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
    assert math.isclose(abs(area(ring)), 1.0)


def test_contains_square_hole() -> None:
    outer = [[0.0, 0.0], [3.0, 0.0], [3.0, 3.0], [0.0, 3.0]]
    hole_ring = [[1.0, 1.0], [2.0, 1.0], [2.0, 2.0], [1.0, 2.0], [1.0, 1.0]]
    assert contains(outer, hole_ring) != -1


def test_contains_returns_on_first_nonzero_winding() -> None:
    outer = [[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0]]
    hole_ring = [[1.5, 1.5], [2.5, 1.5], [2.5, 2.5], [1.5, 2.5], [1.5, 1.5]]
    assert contains(outer, hole_ring) in (-1, 1)


def test_contains_single_sample_vertex() -> None:
    outer = [[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0]]
    assert contains(outer, [[1.5, 1.5]]) in (-1, 1)


def test_contains_returns_zero_when_all_samples_on_edges() -> None:
    outer = [[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0]]
    hole = [[0.0, 1.0], [0.0, 2.0], [0.0, 3.0], [0.0, 1.0]]
    assert contains(outer, hole) == 0


def test_ring_contains_point_on_outer_segment() -> None:
    outer = [[0.0, 0.0], [4.0, 0.0], [4.0, 4.0], [0.0, 4.0]]
    assert _ring_contains(outer, [2.0, 0.0]) == 0


def test_density_thresholds_getter() -> None:
    assert callable(contourDensity().thresholds())


def test_density_xy_weight_constants() -> None:
    d = contourDensity().x(10).y(20).weight(0.5)
    assert d.x()() == 10.0
    assert d.y()() == 20.0
    assert d.weight()() == 0.5


def test_density_invalid_cell_size() -> None:
    with pytest.raises(ValueError, match="invalid cell size"):
        contourDensity().cellSize(0.5)


def test_density_invalid_bandwidth() -> None:
    with pytest.raises(ValueError, match="invalid bandwidth"):
        contourDensity().bandwidth(-1)


def test_contours_sorted_explicit_thresholds() -> None:
    c = contours().size([2, 2]).thresholds([0.9, 0.1])
    out = c([0.0, 1.0, 0.0, 0.0])
    assert [x["value"] for x in out] == [0.1, 0.9]


def test_finite_above_valid_helpers() -> None:
    assert _finite(None, 0, []) == 0.0
    assert math.isnan(_finite("x", 0, []))
    assert _above(None, 1.0) is False
    assert _above("x", 1.0) is False
    assert _valid(None) == float("-inf")
    assert _valid(float("nan")) == float("-inf")
    assert _valid("z") == float("-inf")


def test_smooth1_division_branches() -> None:
    r = _smooth1(0.5, float("nan"), float("nan"), 1.0)
    assert not math.isnan(r)
    # JS returns x when d is NaN (e.g. 0/0).
    assert _smooth1(0.5, 1.0, 1.0, 1.0) == 0.5


def test_contours_empty_input_auto_thresholds() -> None:
    assert contours().size([2, 2])([]) == []


def test_contours_thresholds_callable_setter() -> None:
    c = contours().thresholds(lambda _vals: [0.25, 0.75])
    out = c.size([2, 2])([0.0, 1.0, 0.0, 1.0])
    assert len(out) == 2 and {x["value"] for x in out} == {0.25, 0.75}


def test_contours_ticks_trim_low_end() -> None:
    # Drive `while len(tz_list) > 1 and tz_list[1] < e0: tz_list.pop(0)` (mirrors JS shift).
    with (
        patch("pyd3js_contour.contours.nice", lambda a, b, c: (a, b)),
        patch(
            "pyd3js_contour.contours.ticks",
            lambda _lo, _hi, _n: [-50.0, -40.0, 0.05, 0.5],
        ),
    ):
        c = contours().size([2, 1]).thresholds(4)
        out = c([0.01, 1.0])
        assert [x["value"] for x in out][:2] == [-40.0, 0.05]


def test_density_numeric_threshold_and_weight_nan() -> None:
    d = contourDensity().size([100, 100]).thresholds(4)
    assert d([]) == []
    d2 = contourDensity().weight(lambda _p: "nope").size([50, 50])
    assert d2([[10.0, 10.0]]) == []


def test_density_callable_xy_thresholds_bandwidth_setter() -> None:
    d = (
        contourDensity()
        .x(lambda p: float(p[0]))
        .y(lambda p: float(p[1]))
        .thresholds(lambda _vals: [1e-9, 1e-8])
        .bandwidth(15.0)
    )
    assert d([[5.0, 5.0]]) != []
    assert d.bandwidth() > 14.0


def test_density_empty_grid_mx_none() -> None:
    d = contourDensity().size([10, 10]).cellSize(1024).thresholds(5)
    assert d([]) == []


def test_density_contours_max_when_grid_empty() -> None:
    cc = contourDensity().size([10, 10]).cellSize(1024).contours([])
    assert cc.max == 0.0


def test_density_contour_fn_roundtrip() -> None:
    d = contourDensity().size([200, 200])
    cc = d.contours([[100.0, 100.0]])
    g = cc(0.01)
    assert g["type"] == "MultiPolygon"
    assert "coordinates" in g


def test_last_row_null_coerces_and_invalid_skipped() -> None:
    c = contours().smooth(False).size([3, 2])
    # dy=2 → last row starts at index 3; None → +0 for last-row GE per JS.
    vals = [1.0, 1.0, 1.0, None]
    out = c.contour(vals, 0.5)
    assert out["type"] == "MultiPolygon"
    vals_bad = [1.0, 1.0, 1.0, object()]
    c.contour(vals_bad, 0.5)
    # Short values: last-row probe index >= len(values).
    c.contour([1.0, 1.0], 0.5)
