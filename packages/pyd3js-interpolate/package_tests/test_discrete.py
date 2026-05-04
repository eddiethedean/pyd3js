from __future__ import annotations

from pyd3js_interpolate import interpolateDiscrete


def test_interpolate_discrete() -> None:
    f = interpolateDiscrete([1, 2, 3])
    assert f(0) == 1
    assert f(0.2) == 1
    assert f(0.6) == 2
    assert f(1) == 3
