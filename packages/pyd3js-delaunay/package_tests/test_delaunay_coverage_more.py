"""Extra cases for Delaunay/Voronoi/Path branches (coverage)."""

from __future__ import annotations

from array import array

import pytest

from pyd3js_delaunay import Delaunay
from pyd3js_delaunay.path import Path


def test_path_negative_radius_raises() -> None:
    p = Path()
    p.moveTo(0, 0)
    with pytest.raises(ValueError, match="negative radius"):
        p.arc(0, 0, -1)


def test_delaunay_two_distinct_points(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0]))
    assert len(d.hull) <= 2
    assert d.render() is not None


def test_delaunay_collinear_then_jitter(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 2.0, 0.0]))
    assert d.collinear is None or len(d.collinear) >= 3


def test_delaunay_from_iterable(require_node_mesh: None) -> None:
    def pts():
        yield (0.0, 0.0)
        yield (1.0, 0.0)
        yield (0.5, 1.0)

    d = Delaunay.from_points(pts())
    assert len(d.hull) >= 3


def test_delaunay_render_points(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]))
    s = d.render_points(r=1.5)
    assert s is not None and "A" in s


def test_delaunay_render_points_context_only(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]))
    p = Path()
    d.render_points(p, 2)
    assert "M" in (p.value() or "")


def test_delaunay_triangle_iterator(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]))
    polys = list(d.triangle_polygons())
    assert len(polys) >= 1


def test_voronoi_update(require_node_mesh: None) -> None:
    coords = array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    d = Delaunay(coords)
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    coords[0] = 0.02
    v.update()
    assert v.circumcenters is not None


def test_voronoi_render_empty_when_hull_tiny(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    assert v.render() is None


def test_delaunay_find_nan(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]))
    assert d.find(float("nan"), 0.0) == -1


def test_voronoi_contains_bad_coords(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    assert v.contains(0, float("nan"), 0.0) is False
