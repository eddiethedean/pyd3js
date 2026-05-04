from __future__ import annotations

import math

from pyd3js_interpolate import interpolateNumber
from pyd3js_interpolate.number import coerce_unary_plus


def test_interpolate_number() -> None:
    f = interpolateNumber(10, 20)
    assert math.isclose(f(0), 10)
    assert math.isclose(f(0.5), 15)
    assert math.isclose(f(1), 20)


def test_coerce_unary_plus_and_per_tick_a() -> None:
    class Box:
        def __init__(self, v: float) -> None:
            self._v = v

        def valueOf(self) -> float:
            return float(self._v)

    assert coerce_unary_plus(Box(2.5)) == 2.5
    assert math.isnan(coerce_unary_plus(object()))
    g = interpolateNumber(Box(0), Box(10))
    assert math.isclose(g(0.5), 5.0)

    class ToStr:
        def __str__(self) -> str:
            return "7"

    assert coerce_unary_plus(ToStr()) == 7.0

    assert math.isnan(coerce_unary_plus(None))
    assert coerce_unary_plus(True) == 1.0
    assert math.isnan(coerce_unary_plus("not a number"))

    class SelfVo:
        def valueOf(self) -> SelfVo:
            return self

    assert math.isnan(coerce_unary_plus(SelfVo()))

    class BadStr:
        def __str__(self) -> str:
            raise RuntimeError("no")

    assert math.isnan(coerce_unary_plus(BadStr()))

    class Chain:
        def __init__(self, n: int) -> None:
            self.n = n

        def valueOf(self) -> Chain | int:
            return self.n if self.n <= 0 else Chain(self.n - 1)

    assert coerce_unary_plus(Chain(5)) == 0.0
    assert math.isnan(coerce_unary_plus(Chain(20)))

    class TsBad:
        def toString(self) -> str:
            return "not-a-float-literal-xyz"

    assert math.isnan(coerce_unary_plus(TsBad()))
