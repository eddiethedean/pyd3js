from __future__ import annotations

import math
from array import array
from datetime import datetime

from pyd3js_color import hsl, rgb

from pyd3js_interpolate import interpolate


def test_interpolate_value() -> None:
    assert interpolate("foo", "bar")(0.5) == "bar"
    assert interpolate("1", "2")(0.5) == "1.5"
    assert interpolate(" 1", " 2")(0.5) == " 1.5"

    assert interpolate("red", "blue")(0.5) == "rgb(128, 0, 128)"
    assert interpolate("#ff0000", "#0000ff")(0.5) == "rgb(128, 0, 128)"
    assert interpolate("rgb(255, 0, 0)", "rgb(0, 0, 255)")(0.5) == "rgb(128, 0, 128)"
    assert (
        interpolate("rgba(100%, 0%, 0%, 0.5)", "rgba(0%, 0%, 100%, 0.7)")(0.5)
        == "rgba(128, 0, 128, 0.6)"
    )

    assert interpolate("red", rgb("blue"))(0.5) == "rgb(128, 0, 128)"
    assert interpolate("red", hsl("blue"))(0.5) == "rgb(128, 0, 128)"

    assert interpolate(["red"], ["blue"])(0.5) == ["rgb(128, 0, 128)"]
    assert interpolate([1], [2])(0.5) == [1.5]

    assert interpolate(1, 2)(0.5) == 1.5
    assert math.isnan(interpolate(1, float("nan"))(0.5))

    assert interpolate({"color": "red"}, {"color": "blue"})(0.5) == {
        "color": "rgb(128, 0, 128)"
    }

    class Num:
        def __init__(self, v: float) -> None:
            self._v = v

        def __float__(self) -> float:
            return float(self._v)

    assert interpolate(1, Num(2))(0.5) == 1.5

    class Box:
        def valueOf(self) -> float:
            return 2.0

    assert interpolate(1, Box())(0.5) == 1.5

    class ProtoBox:
        def __init__(self, foo: float) -> None:
            self.foo = foo

        def valueOf(self) -> float:
            return float(self.foo)

    assert interpolate(ProtoBox(0), ProtoBox(2))(0.5) == 1.0

    class BoolBox:
        def valueOf(self) -> bool:
            return True

    assert interpolate(0, BoolBox())(0.5) == 0.5

    class BrokenValueOf:
        def valueOf(self) -> float:
            raise RuntimeError("nope")

    out_bf = interpolate(0, BrokenValueOf())(0.5)
    assert isinstance(out_bf, dict) and callable(out_bf.get("valueOf"))

    class Str2:
        def __str__(self) -> str:
            return "2"

    assert interpolate(1, Str2())(0.5) == 1.5

    class Ts2:
        def toString(self) -> str:
            return "3"

    assert interpolate(1, Ts2())(0.5) == 2.0

    i = interpolate(datetime(2000, 1, 1), datetime(2000, 1, 2))
    assert i(0.5) == datetime(2000, 1, 1, 12)

    assert interpolate(0, None)(0.5) is None
    assert interpolate(0, True)(0.5) is True
    assert interpolate(0, False)(0.5) is False

    assert interpolate({"foo": 0}, {"foo": 2})(0.5) == {"foo": 1}

    r = interpolate([0, 0], array("d", [-1.0, 1.0]))(0.5)
    assert isinstance(r, array) and r.typecode == "d"


def test_interpolate_value_noproto_value_of_and_to_string() -> None:
    """Port of d3 `value-test.js` noproto + prototype valueOf/toString cases."""

    class _NumProto:
        def valueOf(self) -> float:
            return float(self.foo)

    class NBox(_NumProto):
        pass

    na = NBox()
    na.foo = 0.0
    nb = NBox()
    nb.foo = 2.0
    assert interpolate(na, nb)(0.5) == 1.0

    class _StrNumProto:
        def valueOf(self) -> str:
            return str(self.foo)

    class SNBox(_StrNumProto):
        pass

    sa = SNBox()
    sa.foo = 0.0
    sb = SNBox()
    sb.foo = 2.0
    assert interpolate(sa, sb)(0.5) == 1.0

    class _StrBarProto:
        def valueOf(self) -> str:
            return str(self.foo)

    class BarBox(_StrBarProto):
        pass

    ba = BarBox()
    ba.foo = "bar"
    bb = BarBox()
    bb.foo = "baz"
    out_v = interpolate(ba, bb)(0.5)
    assert out_v["foo"] == "baz"
    assert out_v["valueOf"] == {}

    class _ToStrNumProto:
        def toString(self) -> str:
            return str(self.foo)

    class TNBox(_ToStrNumProto):
        pass

    ta = TNBox()
    ta.foo = 0.0
    tb = TNBox()
    tb.foo = 2.0
    assert interpolate(ta, tb)(0.5) == 1.0

    class _ToStrBarProto:
        def toString(self) -> str:
            return str(self.foo)

    class TBBox(_ToStrBarProto):
        pass

    xa = TBBox()
    xa.foo = "bar"
    xb = TBBox()
    xb.foo = "baz"
    out_t = interpolate(xa, xb)(0.5)
    assert out_t["foo"] == "baz"
    assert out_t["toString"] == {}
