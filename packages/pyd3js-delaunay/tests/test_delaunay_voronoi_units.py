from __future__ import annotations

from array import array

import pytest

from pyd3js_delaunay import Delaunay
from pyd3js_delaunay.voronoi import Voronoi


def test_voronoi_invalid_bounds_raises() -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]))
    with pytest.raises(ValueError, match="invalid bounds"):
        Voronoi(d, [1.0, 1.0, 0.0, 0.0])


def test_voronoi_contains_and_neighbors_triangle(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    cx, cy = 0.25, 0.25
    found = None
    for i in range(3):
        if v.contains(i, cx, cy):
            found = i
            break
    assert found is not None
    assert list(v.neighbors(found))


def test_delaunay_find(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.5, 0.9]))
    i = d.find(0.4, 0.4, 0)
    assert 0 <= i < 3


def test_delaunay_render_and_hull(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 2.0, 0.0, 1.0, 1.5]))
    r = d.render()
    assert r is not None and "M" in r
    hp = d.hull_polygon()
    assert hp is not None


def test_voronoi_cell_polygons_index(require_node_mesh: None) -> None:
    d = Delaunay(array("d", [0.0, 0.0, 1.0, 0.0, 0.3, 0.8]))
    v = d.voronoi([0.0, 0.0, 1.0, 1.0])
    cells = list(v.cell_polygons())
    indices = {c.index for c in cells}
    assert indices <= {0, 1, 2}


def test_delaunay_from_points_tuple(require_node_mesh: None) -> None:
    d = Delaunay.from_points([(0, 0), (1, 0), (0.2, 1)])
    assert len(d.hull) >= 2


def test_delaunay_update(require_node_mesh: None) -> None:
    coords = array("d", [0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    d = Delaunay(coords)
    coords[0] = 0.01
    d.update()
    assert len(d.triangles) == len(d.halfedges)
