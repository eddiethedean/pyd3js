from __future__ import annotations

from array import array

import pytest

from pyd3js_delaunay._delaunator import Delaunator


def test_delaunator_init_list_coords_and_update() -> None:
    d = Delaunator([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    assert len(d.triangles) == 3
    d.update()
    assert len(d.triangles) == 3


def test_delaunator_rejects_non_numeric_array_contents() -> None:
    bad = array("u", "abcd")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Expected coords to contain numbers"):
        Delaunator(bad)  # type: ignore[arg-type]


def test_delaunator_from_points_sequence_and_iterable() -> None:
    d1 = Delaunator.from_points([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
    assert len(d1.coords) == 6

    def gen():
        yield (0.0, 0.0)
        yield (1.0, 0.0)
        yield (0.0, 1.0)

    d2 = Delaunator.from_points(gen())
    assert len(d2.coords) == 6


def test_delaunator_empty_coords() -> None:
    d = Delaunator([])
    assert len(d.triangles) == 0
    assert len(d.hull) == 0
