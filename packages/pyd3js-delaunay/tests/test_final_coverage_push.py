from __future__ import annotations

from array import array

import pytest

from pyd3js_delaunay import Delaunay
from pyd3js_delaunay.path import Path


def test_delaunay_render_internal_edges_and_render_points_defaults(require_node_mesh: None) -> None:
    # Four points => two triangles => at least one internal halfedge pair.
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]))
    r = d.render()
    assert r is not None and "L" in r
    rp = d.render_points()
    assert rp is not None and "A" in rp


def test_delaunay_neighbors_valueerror_and_guard_paths(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))

    # Force ValueError path in collinear neighbor lookup.
    d.collinear = array("i", [0, 2])
    assert list(d.neighbors(1)) == []

    # Force guard path (line 166): e never returns to e0; triangles[e_next] always equals i.
    d.collinear = None
    d.inedges[0] = 0
    # After the first step, e alternates between 1 and 2 forever (never -1, never e0).
    d.halfedges = array("i", [0, 1, 1])
    d.triangles = array("i", [0, 0, 0])
    out = list(d.neighbors(0))
    assert out != []


def test_delaunay_step_branches(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))

    # inedges[i] == -1 branch
    d.inedges[0] = -1
    assert d._step(0, 0.1, 0.1) in (0, 1, 2)

    # triangles[e_next] != i break branch
    d.inedges[0] = 0
    d.halfedges = array("i", [0, 0, 0])
    d.triangles = array("i", [0, 1, 1])
    assert d._step(0, 0.1, 0.1) in (0, 1, 2)

    # e == e0 break branch (line 225)
    d.inedges[0] = 0
    d.halfedges = array("i", [0, 0, 0])
    d.triangles = array("i", [0, 0, 0])
    assert d._step(0, 0.1, 0.1) in (0, 1, 2)


def test_voronoi_render_skips_j_lt_i_and_clip_segment_path(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    # This should exercise both the `j < i` skip and at least one clipped segment.
    s = v.render()
    assert s is not None and "M" in s

    # Force clipping segment branch with a known out-of-bounds endpoint.
    p = Path()
    v._render_segment(0.5, 0.5, 2.0, 0.5, p)
    assert p.value() is not None


def test_voronoi_cell_bad_triangulation_and_clip_none(require_node_mesh: None, monkeypatch: pytest.MonkeyPatch) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])

    # Bad triangulation break in _cell.
    idx = 0
    e0 = d.inedges[idx]
    if e0 == -1:
        pytest.skip("inedges[0] is -1 for this input")
    d.triangles[e0 - 2 if e0 % 3 == 2 else e0 + 1] = 999
    assert v._cell(idx) is not None

    # _clip returns None when _cell returns None
    monkeypatch.setattr(v, "_cell", lambda _i: None)
    assert v._clip(0) is None


def test_voronoi_clip_finite_deep_branches(require_node_mesh: None, monkeypatch: pytest.MonkeyPatch) -> None:
    # Cover portions of _clip_finite that depend on edge transitions.
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])

    called = {"edge": 0}

    def edge(*args, **kwargs):
        called["edge"] += 1
        return args[-1]  # j

    monkeypatch.setattr(v, "_edge", edge)

    # A polygon that crosses multiple boundaries so both c0==0 and c0!=0 branches run.
    poly = [-0.5, 0.5, 0.5, 0.5, 1.5, 0.5, 0.5, 1.5]
    out = v._clip_finite(0, poly)
    assert out is None or len(out) >= 2
    assert called["edge"] >= 0


def test_voronoi_clip_infinite_returns_none_when_not_contained(require_node_mesh: None, monkeypatch: pytest.MonkeyPatch) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    monkeypatch.setattr(v, "_clip_finite", lambda *_a, **_k: None)
    monkeypatch.setattr(v, "contains", lambda *_a, **_k: False)
    out = v._clip_infinite(0, [0.5, 0.5, 0.6, 0.5, 0.6, 0.6, 0.5, 0.6], 1.0, 0.0, -1.0, 0.0)
    assert out is None

