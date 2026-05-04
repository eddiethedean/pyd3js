from __future__ import annotations

import math
from array import array

from pyd3js_interpolate import interpolate


def test_interpolate_number_array() -> None:
    r = interpolate([0, 0], array("d", [-1.0, 1.0]))(0.5)
    assert isinstance(r, array)
    assert r.typecode == "d"
    assert math.isclose(r[0], -0.5)
    assert math.isclose(r[1], 0.5)

    r = interpolate([0, 0], array("f", [-1.0, 1.0]))(0.5)
    assert r.typecode == "f"

    r = interpolate([0, 0], array("I", [2**32 - 2, 2]))(0.5)
    assert r.typecode == "I"
    assert r[0] == 2**31 - 1
    assert r[1] == 1

    r = interpolate([0, 0], array("B", [254, 2]))(0.5)
    assert r.typecode == "B"
    assert r[0] == 2**7 - 1
    assert r[1] == 1

    buf = array("d", [-1.0, 1.0])
    mv = memoryview(buf)
    r_mv = interpolate([0, 0], mv)(0.5)
    assert isinstance(r_mv, memoryview)
    assert math.isclose(r_mv[0], -0.5)
    assert math.isclose(r_mv[1], 0.5)
