from __future__ import annotations

from array import array

import pytest

from pyd3js_delaunay import Delaunay


def test_voronoi_default_bounds_branch(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    v = d.voronoi()
    assert v.render_bounds() is not None


def test_neighbors_collinear_branch(require_node_mesh: None) -> None:
    # Collinear points trigger `self.collinear` and the special neighbors behavior.
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 2.0, 0.0, 3.0, 0.0]))
    assert d.collinear is not None
    # Middle point should have two neighbors (prev/next in sorted order).
    n = list(d.neighbors(1))
    assert n == [0, 2]


def test_neighbors_coincident_point_returns_empty(require_node_mesh: None) -> None:
    # Duplicate points: one will be treated as coincident (inedges == -1).
    d = Delaunay(array("d", [0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    # Find an index with inedges == -1.
    idx = None
    for i, e in enumerate(d.inedges):
        if e == -1:
            idx = i
            break
    if idx is None:
        pytest.skip("No coincident point produced by delaunator for this input.")
    assert list(d.neighbors(idx)) == []


def test_step_distance_improves_branch(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0, 0.8, 0.9]))
    # Choose a point closer to some neighbor than the starting index.
    out = d._step(0, 0.9, 0.1)
    assert 0 <= out < (len(d.points) >> 1)


def test_render_hull_default_context(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    assert d.render_hull() is not None


def test_render_triangle_default_context(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    assert d.render_triangle(0) is not None


def test_render_points_overload_r_only(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    # When called with a single numeric arg, it is treated as r.
    s = d.render_points(5)
    assert s is not None and "A" in s


def test_neighbors_guard_and_bad_triangulation_paths(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.2, 1.0]))
    # Corrupt mesh (but keep arrays consistent) to force:
    # - bad triangulation return (triangles[e_next] != i)
    # - guard return after too many iterations
    d.inedges[0] = 0

    d.halfedges = array("i", [0, 0, 0])
    d.triangles = array("i", [1, 1, 1])
    assert list(d.neighbors(0)) == [1]

    d.halfedges = array("i", [0, 0, 0])
    d.triangles = array("i", [0, 0, 0])
    assert list(d.neighbors(0)) != []
