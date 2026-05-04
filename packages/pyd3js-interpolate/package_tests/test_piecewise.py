from __future__ import annotations

from pyd3js_interpolate import interpolate, piecewise


def test_piecewise() -> None:
    i = piecewise(interpolate, [0, 2, 10])
    assert i(-1) == -4
    assert i(0) == 0
    assert i(0.19) == 0.76
    assert i(0.21) == 0.84
    assert i(0.5) == 2
    assert i(0.75) == 6
    assert i(1) == 10

    i = piecewise([0, 2, 10])
    assert i(-1) == -4

    i = piecewise(["a0", "a2", "a10"])
    assert i(-1) == "a-4"
    assert i(0) == "a0"
    assert i(0.19) == "a0.76"
    assert i(1) == "a10"
