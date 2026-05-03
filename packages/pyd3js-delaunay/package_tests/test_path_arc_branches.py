from __future__ import annotations

from pyd3js_delaunay.path import Path


def test_arc_r_zero_when_empty_adds_move_and_returns() -> None:
    p = Path()
    p.arc(2, 3, 0)
    # Should create a move-to to x0,y0 and then return (no arc command).
    v = p.value() or ""
    assert v.startswith("M")
    assert "A" not in v


def test_arc_r_zero_when_has_current_point_may_add_line() -> None:
    p = Path()
    p.moveTo(0, 0)
    p.arc(2, 3, 0)
    v = p.value() or ""
    # If current point differs from x0,y0, arc() emits a line-to before returning.
    assert "L" in v
    assert "A" not in v
