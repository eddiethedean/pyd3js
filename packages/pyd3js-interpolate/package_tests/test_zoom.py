from __future__ import annotations

import math

from pyd3js_interpolate import interpolateZoom


def _assert_in_delta(actual: object, expected: object, delta: float = 1e-6) -> None:
    if isinstance(expected, list):
        assert isinstance(actual, list)
        assert len(actual) == len(expected)
        for x, y in zip(actual, expected, strict=True):
            _assert_in_delta(x, y, delta)
        return
    assert isinstance(actual, (int, float))
    assert isinstance(expected, (int, float))
    assert expected - delta <= actual <= expected + delta


def test_interpolate_zoom() -> None:
    z = interpolateZoom(
        [324.68721096803614, 59.43501602433761, 1.8827137399562621],
        [324.6872108946794, 59.43501601062763, 7.399052110984391],
    )(0.5)
    _assert_in_delta(
        z, [324.68721093135775, 59.43501601748262, 3.7323313186268305], 1e-10
    )

    _assert_in_delta(interpolateZoom([0, 0, 1], [0, 0, 1.1]).duration, 67, 1)
    _assert_in_delta(interpolateZoom([0, 0, 1], [0, 0, 2]).duration, 490, 1)
    _assert_in_delta(interpolateZoom([0, 0, 1], [10, 0, 8]).duration, 2872.5, 1)

    _assert_in_delta(
        interpolateZoom([0, 0, 1], [10, 10, 5])(0.5),
        interpolateZoom.rho(math.sqrt(2))([0, 0, 1], [10, 10, 5])(0.5),
        1e-10,
    )

    interp = interpolateZoom.rho(0)([0, 0, 1], [10, 0, 8])
    _assert_in_delta(interp(0.5), [1.111, 0, math.sqrt(8)], 1e-3)
    assert round(interp.duration) == 1470

    interp2 = interpolateZoom.rho(2)([0, 0, 1], [10, 0, 8])
    _assert_in_delta(interp2(0.5), [1.111, 0, 12.885], 1e-3)
    assert round(interp2.duration) == 3775
