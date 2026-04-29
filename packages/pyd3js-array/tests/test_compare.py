from __future__ import annotations

import math

from pyd3js_array._compare import definite, gt, lt, tonumber


class _ObjValueOf:
    def __init__(self, value: object) -> None:
        self._value = value

    def valueOf(self) -> object:
        return self._value


class _ObjValueOfRaises:
    def valueOf(self) -> object:
        raise RuntimeError("boom")


class _EqRaises:
    def __eq__(self, other: object) -> bool:
        raise RuntimeError("boom")


def test_tonumber_basics() -> None:
    assert math.isnan(tonumber(None))
    assert tonumber(True) == 1.0
    assert tonumber(False) == 0.0
    assert tonumber(3) == 3.0
    assert tonumber(3.5) == 3.5


def test_tonumber_strings() -> None:
    assert tonumber(" 2 ") == 2.0
    assert math.isnan(tonumber(""))
    assert math.isnan(tonumber("   "))
    assert math.isnan(tonumber("nope"))


def test_tonumber_valueof() -> None:
    assert tonumber(_ObjValueOf(" 4 ")) == 4.0
    assert math.isnan(tonumber(_ObjValueOf(None)))
    assert math.isnan(tonumber(object()))


def test_definite_variants() -> None:
    assert definite(1) is True
    assert definite(None) is False
    assert definite(float("nan")) is False
    assert definite(_ObjValueOf(1)) is True
    assert definite(_ObjValueOf(float("nan"))) is False
    assert definite(_ObjValueOfRaises()) is False
    assert definite(_EqRaises()) is False


def test_relational_helpers() -> None:
    assert gt("b", "a") is True
    assert lt("a", "b") is True
    assert gt("2", "10") is True  # string comparison branch
    assert gt(2, "10") is False  # numeric coercion branch
    assert gt("nope", 1) is False  # NaN coerces to false
    assert lt("nope", 1) is False

