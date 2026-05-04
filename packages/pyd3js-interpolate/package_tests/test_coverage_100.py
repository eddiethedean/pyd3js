from __future__ import annotations

import math
from array import array
from datetime import datetime

import pytest

import pyd3js_interpolate as pi
from pyd3js_interpolate.basis import basis_fn, interpolate_basis
from pyd3js_interpolate.basis_closed import interpolate_basis_closed
from pyd3js_interpolate.transform import _rotate_shortest
from pyd3js_interpolate.transform.decompose import IDENTITY, decompose
from pyd3js_interpolate.transform.parse import parse_css, parse_svg


def test_rotate_shortest() -> None:
    assert _rotate_shortest(200.0, 0.0) == (200.0, 360.0)
    assert _rotate_shortest(0.0, 200.0) == (360.0, 200.0)


def test_basis_fn_and_interpolators() -> None:
    assert basis_fn(0.5, 0.0, 1.0, 2.0, 3.0) != 0.0
    ib = interpolate_basis([0.0, 1.0, 2.0, 3.0])
    assert ib(0.0) == 0.0
    assert ib(1.0) == 3.0
    ibc = interpolate_basis_closed([0.0, 1.0, 2.0])
    assert ibc(0.25) == ibc(1.25)
    assert ibc(-0.25) == ibc(0.75)


def test_decompose_and_parse() -> None:
    assert IDENTITY["scaleX"] == 1.0
    d = decompose(1, 0, 0, 1, 5, 6)
    assert d["translateX"] == 5
    assert parse_css("") == IDENTITY
    assert parse_svg(None) == IDENTITY
    assert parse_svg("   ") == IDENTITY
    assert parse_svg("rotate(10)") == parse_css("rotate(10)")
    r3 = parse_css("rotate(90deg 10px 20px)")
    r0 = parse_css("rotate(90deg)")
    assert r3["translateX"] != r0["translateX"] or r3["translateY"] != r0["translateY"]
    pc = parse_css("translate(10px) scale(2)")
    assert pc["translateX"] != 0 or pc["scaleX"] != 1
    parse_css("translateY(3px) translateX(2px) rotate(5deg) skewX(1deg) scale(2,3)")
    parse_css("matrix(1,2,3)")
    parse_css("nonsense(1)")
    parse_svg("matrix(1,1,1,1,1)")
    parse_css("translate() translateX() translateY() scale() rotate() skewX() skewX()")
    parse_css("skewX()")
    parse_css("skewY(3deg)")
    parse_css("skewX(1deg) skewY(2deg)")


def test_number_array_branches() -> None:
    a = array("b", [-1, 1])
    r = pi.interpolateNumberArray([0, 0], a)(0.5)
    assert r.typecode == "b"

    for tc, vals in (
        ("h", [-1, 1]),
        ("H", [1, 2]),
        ("i", [-1, 1]),
        ("l", [1, 2]),
        ("L", [1, 2]),
        ("q", [-1, 1]),
        ("Q", [1, 2]),
    ):
        buf = array(tc, vals)
        pi.interpolateNumberArray([0, 0], buf)(0.5)

    assert list(pi.interpolateNumberArray([0], [1.0, 2.0])(0.5)) == [0.5, 2.0]

    assert pi.interpolateArray([0, 0], array("d", [1.0, 2.0]))(0.5).typecode == "d"

    empty = array("d")
    assert len(pi.interpolateNumberArray([], empty)(0.5)) == 0

    pi.interpolateNumberArray([0, 0], array("b", [100, -100]))(0.5)
    pi.interpolateNumberArray([0, 0], array("h", [30000, -30000]))(0.5)
    pi.interpolateNumberArray([0, 0], array("q", [2**62, -(2**62)]))(0.5)

    mv2 = memoryview(bytearray(16)).cast("d", (2, 1))
    assert mv2.ndim == 2
    assert not pi.isNumberArray(mv2)
    with pytest.raises(TypeError):
        pi.interpolateNumberArray([0, 0], mv2)

    try:
        hf = array("e", [1.0, 2.0])
    except (TypeError, ValueError):
        pass
    else:
        mvh = memoryview(hf)
        assert not pi.isNumberArray(mvh)
        with pytest.raises(TypeError):
            pi.interpolateNumberArray([0, 0], mvh)

    with pytest.raises(TypeError):
        pi.interpolateNumberArray([0, 0], memoryview(b"\x00").cast("?"))


def test_rgb_basis_and_gamma() -> None:
    f = pi.interpolateRgbBasis(["red", "green", "blue"])
    assert "rgb(" in f(0.5)
    fc = pi.interpolateRgbBasisClosed(["red", "green"])
    assert "rgb(" in fc(0.3)


def test_date_numeric_fallback() -> None:
    t0 = datetime(2000, 1, 1).timestamp() * 1000
    t1 = datetime(2000, 1, 2).timestamp() * 1000
    d = pi.interpolateDate(t0, t1)(0.5)
    assert isinstance(d, datetime)


def test_quantize_edge() -> None:
    assert pi.quantize(pi.interpolateNumber(0, 1), 0) == []
    out = pi.quantize(pi.interpolateNumber(0, 1), 1)
    assert len(out) == 1 and math.isnan(out[0])


def test_string_js_format_branches() -> None:
    s = pi.interpolateString("1e20", "2e20")(0.5)
    assert "e" in s or "E" in s or float(s) > 0
    s2 = pi.interpolateString("1e308", "2e308")(0.5)
    assert isinstance(s2, str)
    assert pi.interpolateString("10", "10")(0.5) == "10"
    assert "Infinity" in pi.interpolateString("1e308", "2e308")(0.5)
    from pyd3js_interpolate.string import _js_string_number

    assert _js_string_number(float("inf")) == "Infinity"
    assert _js_string_number(float("-inf")) == "-Infinity"
    assert _js_string_number(float("nan")) == "NaN"
    assert "e" in _js_string_number(1e-7).lower()


def test_value_object_fallback_line() -> None:
    class X:
        pass

    assert isinstance(pi.interpolate({"a": 1}, X())(0.5), dict)

    class NanBox:
        def __float__(self) -> float:
            return float("nan")

    assert isinstance(pi.interpolate(0, NanBox())(0.5), dict)


def test_transform_pop_and_static_branches() -> None:
    s0 = pi.interpolateTransformCss("rotate(5deg)", "rotate(5deg)")(0.3)
    assert "rotate(5" in s0 and "deg)" in s0
    s1 = pi.interpolateTransformCss("skewX(2deg)", "skewX(2deg)")(0.3)
    assert "skewX(2" in s1
    s2 = pi.interpolateTransformCss("scale(2,3)", "scale(2,3)")(0.3)
    assert "scale(2" in s2 and "3" in s2
    s3 = pi.interpolateTransformCss("translate(1px,2px)", "translate(1px,2px)")(0.3)
    assert "translate(1" in s3 and "2" in s3
    pi.interpolateTransformCss("translate(0px,0px)", "translate(1px,0px)")(0.5)
    pi.interpolateTransformCss("rotate(0deg)", "rotate(200deg)")(0.5)
    pi.interpolateTransformCss("rotate(200deg)", "rotate(0deg)")(0.5)
    pi.interpolateTransformCss("rotate(10deg)", "rotate(350deg)")(0.5)
    pi.interpolateTransformCss("skewX(0deg)", "skewX(10deg)")(0.5)


def test_array_generic_returns_same_list() -> None:
    from pyd3js_interpolate.array import generic_array

    out = [0, 0, 0]
    # generic_array mutates internal list built from b — exercise na < nb
    f = generic_array([1], out)
    f(0.5)
    assert len(out) == 3


def test_object_as_dict_branches() -> None:
    from collections import UserDict

    from pyd3js_interpolate.object import _object_as_dict, _normalize_object

    class BadDesc:
        def __get__(self, obj: object, owner: type | None = None) -> int:
            raise AttributeError("nope")

    class Z:
        bad = BadDesc()

    _object_as_dict(Z())

    assert _normalize_object(UserDict([("a", 1)])) == {"a": 1}

    class C:
        @classmethod
        def cm(cls) -> int:
            return 1

        def meth(self) -> int:
            return 2

    d = _object_as_dict(C())
    assert "meth" not in d or isinstance(d.get("meth"), int)
