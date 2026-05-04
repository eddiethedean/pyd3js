from __future__ import annotations

from pyd3js_interpolate import interpolateRound


def test_interpolate_round() -> None:
    f = interpolateRound(10, 20)
    assert f(0) == 10
    assert f(0.5) == 15
    assert f(1) == 20
