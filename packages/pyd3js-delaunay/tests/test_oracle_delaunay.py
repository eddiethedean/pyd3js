"""Compare Delaunay / Voronoi to the bundled d3 oracle."""

from __future__ import annotations

import re
from array import array

import pytest

from pyd3js_delaunay import Delaunay


def _path_numbers(s: str | None) -> list[float]:
    if not s:
        return []
    return [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?(?:e[-+]?\d+)?", s)]


def _mesh_expr(coords: list[float]) -> str:
    parts = ",".join(str(float(x)) for x in coords)
    # Flat coords must use `new d3.Delaunay(coords)`, not `.from` (which treats input as points array).
    return f"""(function(){{
  const coords = Float64Array.of({parts});
  const d = new d3.Delaunay(coords);
  return {{
    hull: Array.from(d.hull),
    triangles: Array.from(d.triangles),
    halfedges: Array.from(d.halfedges),
  }};
}})()"""


def _vor_render_expr(coords: list[float], bounds: list[float]) -> str:
    c = ",".join(str(float(x)) for x in coords)
    b = ",".join(str(float(x)) for x in bounds)
    return f"""(function(){{
  const coords = Float64Array.of({c});
  const d = new d3.Delaunay(coords);
  const v = d.voronoi([{b}]);
  return {{ render: v.render(), renderBounds: v.renderBounds() }};
}})()"""


@pytest.mark.oracle
def test_delaunay_mesh_matches_oracle_triangle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    coords = [0.0, 0.0, 1.0, 0.0, 0.0, 1.0]
    js = oracle_eval(_mesh_expr(coords))
    d = Delaunay(array("d", coords))
    assert list(d.hull) == js["hull"]
    assert list(d.triangles) == js["triangles"]
    assert list(d.halfedges) == js["halfedges"]


@pytest.mark.oracle
def test_delaunay_mesh_matches_oracle_many_points(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    coords: list[float] = []
    for i in range(11):
        coords.extend([i * 0.3, (i * 13) % 7 * 0.2])

    js = oracle_eval(_mesh_expr(coords))
    d = Delaunay(array("d", coords))
    assert list(d.hull) == js["hull"]
    assert list(d.triangles) == js["triangles"]
    assert list(d.halfedges) == js["halfedges"]


@pytest.mark.oracle
def test_voronoi_render_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    coords = [0.0, 0.0, 1.0, 0.0, 0.5, 0.8]
    bounds = [0.0, 0.0, 1.0, 1.0]
    js = oracle_eval(_vor_render_expr(coords, bounds))
    d = Delaunay(array("d", coords))
    v = d.voronoi(bounds)
    assert _path_numbers(v.render()) == pytest.approx(
        _path_numbers(js["render"]), rel=1e-9, abs=1e-9
    )
    assert _path_numbers(v.render_bounds()) == pytest.approx(
        _path_numbers(js["renderBounds"]), rel=1e-9, abs=1e-9
    )
