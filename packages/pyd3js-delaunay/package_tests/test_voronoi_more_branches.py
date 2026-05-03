from __future__ import annotations

from array import array

import pytest

from pyd3js_delaunay import Delaunay
from pyd3js_delaunay.path import Path
from pyd3js_delaunay.voronoi import Voronoi


def test_voronoi_default_bounds(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = Voronoi(d)
    assert v.render_bounds() is not None


def test_render_cell_buffer_and_early_return(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])

    monkeypatch.setattr(v, "_clip", lambda _i: None)
    assert v.render_cell(0) is None


def test_render_cell_dedup_loop(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])

    # First == last to hit the while loop; also includes a duplicate vertex to skip lineTo.
    pts = [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0]
    monkeypatch.setattr(v, "_clip", lambda _i: pts)
    out = v.render_cell(0)
    assert out is not None


def test_render_segment_inside_box_branch(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    p = Path()
    v._render_segment(0.1, 0.1, 0.9, 0.9, p)
    assert "L" in (p.value() or "")


def test_neighbors_returns_early_when_clip_none(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    monkeypatch.setattr(v, "_clip", lambda _i: None)
    assert list(v.neighbors(0)) == []


def test_neighbors_skips_when_other_cell_missing(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    real_clip = v._clip

    def clip(i: int):
        if i == 0:
            return real_clip(i)
        return None

    monkeypatch.setattr(v, "_clip", clip)
    assert list(v.neighbors(0)) == []


def test_cell_circumcenters_none_branch(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    v.circumcenters = None
    assert v._cell(0) is None


def test_cell_e0_minus_one_branch(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    idx = None
    for i, e in enumerate(d.inedges):
        if e == -1:
            idx = i
            break
    if idx is None:
        pytest.skip("No coincident point produced by delaunator for this input.")
    assert v._cell(idx) is None


def test_clip_degenerate_single_point_returns_bounds(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    out = v._clip(0)
    assert out is not None and len(out) == 8


def test_clip_calls_finite_path_for_interior_point(require_node_mesh: None) -> None:
    # Need at least one interior point (not on the hull) so vv[v] == vv[v+1] == 0.
    coords = []
    for x, y in [(0, 0), (1, 0), (1, 1), (0, 1), (0.5, 0.5)]:
        coords.extend([float(x), float(y)])
    d = Delaunay(array("d", coords))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    interior = None
    hull_set = set(d.hull)
    for i in range(len(d.points) // 2):
        if i not in hull_set:
            interior = i
            break
    if interior is None:
        pytest.skip("No interior point available for this input.")
    assert v._clip(interior) is not None


def test_clip_finite_box_fallback_branch(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    monkeypatch.setattr(v, "contains", lambda *_a, **_k: True)
    # A polygon entirely outside => clipping yields None, so we fall back to returning the bounds box.
    out = v._clip_finite(0, [-2.0, -2.0, -3.0, -3.0])
    assert out is not None and len(out) == 8


def test_clip_finite_continue_and_first_assignment_lines(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])

    calls = {"n": 0}

    def clip_segment(*args, **kwargs):
        calls["n"] += 1
        # First time: force the `continue` path (line 283).
        if calls["n"] == 1:
            return None
        return [0.0, 0.0, 1.0, 0.0]

    monkeypatch.setattr(v, "_clip_segment", clip_segment)
    # A polygon with at least one out-of-bounds vertex so the c0==0 branch is used.
    out = v._clip_finite(0, [0.5, 0.5, 2.0, 0.5, 0.5, 0.5])
    assert out is None or len(out) >= 2


def test_clip_finite_sets_p_from_sx1_when_first_edge_inside_to_outside(
    require_node_mesh: None,
) -> None:
    # This targets the `else: p = [sx1, sy1]` branch (voronoi.py line 303).
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    out = v._clip_finite(0, [2.0, 0.5, 0.5, 0.5])
    assert out is None or len(out) >= 2


def test_clip_segment_math_branches(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])

    # top (non-zero dy)
    c0 = v._regioncode(0.2, -1.0)
    c1 = v._regioncode(0.8, 0.5)
    assert v._clip_segment(0.2, -1.0, 0.8, 0.5, c0, c1) is not None

    # bottom
    c0 = v._regioncode(0.2, 2.0)
    c1 = v._regioncode(0.8, 0.5)
    assert v._clip_segment(0.2, 2.0, 0.8, 0.5, c0, c1) is not None

    # right (non-zero dx)
    c0 = v._regioncode(2.0, 0.2)
    c1 = v._regioncode(0.5, 0.8)
    assert v._clip_segment(2.0, 0.2, 0.5, 0.8, c0, c1) is not None

    # left
    c0 = v._regioncode(-1.0, 0.2)
    c1 = v._regioncode(0.5, 0.8)
    assert v._clip_segment(-1.0, 0.2, 0.5, 0.8, c0, c1) is not None


def test_clip_segment_guard_lines_and_iteration_limit(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])

    # Hit each division-by-zero guard line explicitly.
    # top dy == 0
    assert v._clip_segment(0.0, 2.0, 1.0, 2.0, 0b1000, 0) is None
    # bottom dy == 0
    assert v._clip_segment(0.0, -1.0, 1.0, -1.0, 0b0100, 0) is None
    # right dx == 0
    assert v._clip_segment(2.0, 0.0, 2.0, 1.0, 0b0010, 0) is None
    # left dx == 0
    assert v._clip_segment(-1.0, 0.0, -1.0, 1.0, 0b0001, 0) is None

    # Hit the 64-iteration limit return (line 364) by forcing c0=0 and c1 to remain non-zero.
    monkeypatch.setattr(v, "_regioncode", lambda *_a, **_k: 0b0001)
    assert v._clip_segment(1.0, 0.0, -1.0, 1.0, 0, 0b0001) is None


def test_clip_infinite_guard_break_and_box_fallback(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    # Force clip_finite to return a big-ish polygon and then make edgecode always non-zero
    # and edge() make no progress, so the guard path triggers.
    monkeypatch.setattr(v, "_clip_finite", lambda _i, p: list(p))  # type: ignore[assignment]
    monkeypatch.setattr(v, "_edgecode", lambda *_a, **_k: 0b0001)  # type: ignore[assignment]
    monkeypatch.setattr(v, "_edge", lambda *_a, **_k: 0)  # type: ignore[assignment]

    pts = [0.5, 0.5, 0.6, 0.5, 0.6, 0.6, 0.5, 0.6]
    out = v._clip_infinite(0, pts, 1.0, 0.0, -1.0, 0.0)
    assert out is not None

    # Force box fallback when clipped is None and contains(center) is True.
    monkeypatch.setattr(v, "_clip_finite", lambda *_a, **_k: None)  # type: ignore[assignment]
    monkeypatch.setattr(v, "contains", lambda *_a, **_k: True)
    out2 = v._clip_infinite(0, pts, 1.0, 0.0, -1.0, 0.0)
    assert out2 is not None and len(out2) == 8


def test_edge_guard_and_break_branches(
    require_node_mesh: None, monkeypatch: pytest.MonkeyPatch
) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    monkeypatch.setattr(v, "contains", lambda *_a, **_k: True)
    p: list[float] = []
    # Use a target edgecode that will never be reached to exercise the guard > 48 break.
    v._edge(0, 0b0101, 0b1111, p, 0)
    # Break branch via invalid code.
    v._edge(0, 123, 456, p, 0)


def test_project_returns_none_when_no_intersection(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    assert v._project(0.5, 0.5, 0.0, 0.0) is None


def test_simplify_short_and_empty_cases(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    assert v._simplify([0.0, 0.0, 1.0, 1.0]) == [0.0, 0.0, 1.0, 1.0]
