from __future__ import annotations

from pyd3js_delaunay.path import Path
from pyd3js_delaunay.polygon import Polygon


def test_path_moves_lines_and_rect() -> None:
    p = Path()
    assert p.value() is None
    p.moveTo(0, 0)
    p.lineTo(1, 2)
    val = p.value() or ""
    assert "M" in val and "L" in val
    p.closePath()
    val2 = p.value()
    assert val2 is not None and val2.endswith("Z")

    r = Path()
    r.rect(1, 2, 3, 4)
    rv = r.value() or ""
    assert "h" in rv and rv.endswith("Z")


def test_path_arc_accepts_extra_args() -> None:
    p = Path()
    p.moveTo(10, 10)
    p.arc(5, 5, 2, 0, 6.28)
    assert "A" in (p.value() or "")


def test_polygon_collects_points() -> None:
    poly = Polygon()
    assert poly.value() is None
    poly.moveTo(0, 0)
    poly.lineTo(1, 0)
    poly.closePath()
    v = poly.value()
    assert v is not None
    assert len(v) == 3
