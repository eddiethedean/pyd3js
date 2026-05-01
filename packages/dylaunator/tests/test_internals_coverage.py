"""Targeted coverage for branches not exercised by upstream JS port tests."""

from __future__ import annotations

from array import array

import pytest

from dylaunator import Delaunator
from dylaunator.delaunator import circumcenter, pseudo_angle


def test_pseudo_angle_zero_vector() -> None:
    assert pseudo_angle(0.0, 0.0) == 0.25


def test_circumcenter_collinear_returns_seed() -> None:
    assert circumcenter(0.0, 0.0, 1.0, 0.0, 2.0, 0.0) == (0.0, 0.0)


def test_from_points_uses_flat_iterable_for_generator() -> None:
    def gen():
        yield (0.0, 0.0)
        yield (1.0, 0.0)
        yield (0.0, 1.0)

    d = Delaunator.from_points(gen())
    assert list(d.triangles) == [0, 2, 1]


def test_constructor_rejects_non_numeric_array_elements() -> None:
    # array('u') elements are length-1 strings, not int/float (Python 3.x)
    with pytest.raises(ValueError, match="Expected coords to contain numbers"):
        Delaunator(array("u", "abcd"))


def test_triangles_len_js_setter() -> None:
    d = Delaunator([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    d.trianglesLen = 0
    assert d.triangles_len == 0
