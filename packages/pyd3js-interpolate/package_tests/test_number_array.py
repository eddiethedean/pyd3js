"""Port of d3-interpolate `test/numberArray-test.js` (v3.0.1) + buffer extensions."""

from __future__ import annotations

import math
from array import array

import pytest

from pyd3js_interpolate import interpolateNumberArray


def test_interpolate_number_array_defined_elements() -> None:
    a = array("d", [2.0, 12.0])
    b = array("d", [4.0, 24.0])
    r = interpolateNumberArray(a, b)(0.5)
    assert r == array("d", [3.0, 18.0])


def test_interpolate_number_array_ignores_extra_a() -> None:
    a = array("d", [2.0, 12.0, 12.0])
    b = array("d", [4.0, 24.0])
    r = interpolateNumberArray(a, b)(0.5)
    assert r == array("d", [3.0, 18.0])


def test_interpolate_number_array_constant_tail_from_b() -> None:
    a = array("d", [2.0, 12.0])
    b = array("d", [4.0, 24.0, 12.0])
    r = interpolateNumberArray(a, b)(0.5)
    assert r == array("d", [3.0, 18.0, 12.0])


def test_interpolate_number_array_none_as_undefined() -> None:
    assert interpolateNumberArray(None, [2.0, 12.0])(0.5) == array("d", [2.0, 12.0])
    assert interpolateNumberArray([2.0, 12.0], None)(0.5) == array("d")
    assert interpolateNumberArray(None, None)(0.5) == array("d")


def test_interpolate_number_array_uses_b_typecode() -> None:
    a64 = array("d", [2.0, 12.0])
    assert interpolateNumberArray(a64, array("d", [4.0, 24.0, 12.0]))(0.5).typecode == "d"
    assert interpolateNumberArray(a64, array("f", [4.0, 24.0, 12.0]))(0.5).typecode == "f"
    assert interpolateNumberArray(a64, array("B", [4, 24, 12]))(0.5).typecode == "B"
    assert interpolateNumberArray(a64, array("H", [4, 24, 12]))(0.5).typecode == "H"


def test_interpolate_number_array_unsigned_bytes() -> None:
    r = interpolateNumberArray(array("B", [1, 12]), array("B", [255, 0]))(0.5)
    assert r == array("B", [128, 6])


def test_interpolate_number_array_exact_ends_large_float() -> None:
    i = interpolateNumberArray(array("d", [2e42]), array("d", [355.0]))
    assert i(0) == array("d", [2e42])
    assert i(1) == array("d", [355.0])


def test_interpolate_number_array_list_b_mixed_length() -> None:
    r = interpolateNumberArray([0], [1.0, 2.0])(0.5)
    assert r == array("d", [0.5, 2.0])


def test_interpolate_number_array_rejects_bad_a() -> None:
    with pytest.raises(TypeError):
        interpolateNumberArray(3, array("d", [1.0]))


def test_interpolate_number_array_rejects_bad_b() -> None:
    with pytest.raises(TypeError):
        interpolateNumberArray([], "not-a-buffer")


def test_interpolate_number_array_empty_memoryview_b() -> None:
    r = interpolateNumberArray(None, memoryview(b""))(0.5)
    assert r == array("d")


def test_interpolate_via_interpolate_import() -> None:
    from pyd3js_interpolate import interpolate

    r = interpolate([0, 0], array("d", [-1.0, 1.0]))(0.5)
    assert isinstance(r, array) and r.typecode == "d"
    assert math.isclose(r[0], -0.5)
    assert math.isclose(r[1], 0.5)

    r = interpolate([0, 0], array("f", [-1.0, 1.0]))(0.5)
    assert r.typecode == "f"

    buf = array("d", [-1.0, 1.0])
    mv = memoryview(buf)
    r_mv = interpolate([0, 0], mv)(0.5)
    assert isinstance(r_mv, memoryview)
    assert math.isclose(r_mv[0], -0.5)
    assert math.isclose(r_mv[1], 0.5)
