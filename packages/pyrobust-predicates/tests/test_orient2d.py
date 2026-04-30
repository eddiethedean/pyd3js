from __future__ import annotations

from pyrobust_predicates import orient2d, orient2dfast


def test_orient2d_matches_fast_for_typical_triangles() -> None:
    pts = [
        (0.0, 0.0, 1.0, 0.0, 0.0, 1.0),
        (0.0, 0.0, 0.0, 1.0, 1.0, 0.0),
        (10.0, 10.0, 20.0, 10.0, 15.0, 18.0),
    ]
    for ax, ay, bx, by, cx, cy in pts:
        assert orient2d(ax, ay, bx, by, cx, cy) == orient2dfast(ax, ay, bx, by, cx, cy)


def test_orient2d_collinear() -> None:
    assert orient2d(0, 0, 1, 0, 2, 0) == 0
