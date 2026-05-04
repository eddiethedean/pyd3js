from __future__ import annotations

from array import array

from pyd3js_interpolate import interpolateArray


def test_interpolate_array() -> None:
    assert interpolateArray([2, 12], [4, 24])(0.5) == [3, 18]
    assert interpolateArray([[2, 12]], [[4, 24]])(0.5) == [[3, 18]]
    assert interpolateArray([{"foo": [2, 12]}], [{"foo": [4, 24]}])(0.5) == [
        {"foo": [3, 18]}
    ]
    assert interpolateArray([2, 12, 12], [4, 24])(0.5) == [3, 18]
    assert interpolateArray([2, 12], [4, 24, 12])(0.5) == [3, 18, 12]
    assert interpolateArray(None, [2, 12])(0.5) == [2, 12]
    assert interpolateArray([2, 12], None)(0.5) == []
    assert interpolateArray(None, None)(0.5) == []

    a = array("d", [2.0, 12.0])
    assert interpolateArray(a, [4, 24])(0.5) == [3, 18]

    a2 = [2e42]
    b2 = [335.0]
    assert interpolateArray(a2, b2)(1) == b2
    assert interpolateArray(a2, b2)(0) == a2
