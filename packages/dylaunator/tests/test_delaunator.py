from __future__ import annotations

from dylaunator import Delaunator


def test_delaunator_example_from_readme() -> None:
    coords = [377, 479, 453, 434, 326, 387, 444, 359, 511, 389, 586, 429, 470, 315, 622, 493, 627, 367, 570, 314]
    d = Delaunator(coords)
    assert list(d.triangles) == [4, 3, 1, 4, 6, 3, 1, 5, 4, 4, 9, 6, 2, 0, 1, 1, 7, 5, 5, 9, 4, 6, 2, 3, 3, 2, 1, 5, 8, 9, 0, 7, 1, 5, 7, 8]


def test_delaunator_collinear_hull() -> None:
    d = Delaunator([0, 0, 1, 0, 2, 0])
    assert len(d.triangles) == 0
    assert list(d.hull) == [0, 1, 2]
