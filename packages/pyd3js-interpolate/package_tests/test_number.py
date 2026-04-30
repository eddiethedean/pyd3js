from __future__ import annotations

import math

from pyd3js_interpolate import interpolateNumber


def test_interpolate_number() -> None:
    f = interpolateNumber(10, 20)
    assert math.isclose(f(0), 10)
    assert math.isclose(f(0.5), 15)
    assert math.isclose(f(1), 20)
