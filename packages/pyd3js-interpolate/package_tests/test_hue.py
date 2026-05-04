from __future__ import annotations

import math

from pyd3js_interpolate import interpolateHue


def test_interpolate_hue() -> None:
    i = interpolateHue("10", "20")
    assert i(0.0) == 10
    assert i(0.2) == 12
    assert i(1.0) == 20

    i = interpolateHue(10, float("nan"))
    assert i(0.5) == 10

    i = interpolateHue(float("nan"), 20)
    assert i(0.5) == 20

    i = interpolateHue(float("nan"), float("nan"))
    assert math.isnan(i(0.5))

    i = interpolateHue(10, 350)
    assert i(0.0) == 10
    assert i(0.2) == 6
    assert i(1.0) == 350
