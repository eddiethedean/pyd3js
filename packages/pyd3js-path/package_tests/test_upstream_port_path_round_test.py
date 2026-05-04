import math
import re

import pytest

from pyd3js_path import path, pathRound


def test_path_round_defaults_to_three_digits() -> None:
    p = pathRound()
    p.moveTo(math.pi, math.e)
    assert str(p) == "M3.142,2.718"


def test_path_round_null_equivalent_to_zero() -> None:
    p = pathRound(None)
    p.moveTo(math.pi, math.e)
    assert str(p) == "M3,3"


def test_path_round_validates_digits() -> None:
    with pytest.raises(ValueError, match="invalid digits"):
        pathRound(float("nan"))
    with pytest.raises(ValueError, match="invalid digits"):
        pathRound(-1)


def test_path_round_ignores_digits_greater_than_15() -> None:
    p = pathRound(40)
    p.moveTo(math.pi, math.e)
    assert str(p) == "M3.141592653589793,2.718281828459045"


def test_path_round_move_to_limits_precision() -> None:
    p = pathRound(1)
    p.moveTo(123.456, 789.012)
    assert str(p) == "M123.5,789"


def test_path_round_line_to_limits_precision() -> None:
    p = pathRound(1)
    p.moveTo(0, 0)
    p.lineTo(123.456, 789.012)
    assert str(p) == "M0,0L123.5,789"


def test_path_round_arc_limits_precision() -> None:
    p0 = path()
    p = pathRound(1)

    p0.arc(10.0001, 10.0001, 123.456, 0, math.pi + 0.0001)
    p.arc(10.0001, 10.0001, 123.456, 0, math.pi + 0.0001)
    assert str(p) == precision(str(p0), 1)

    p0.arc(10.0001, 10.0001, 123.456, 0, math.pi - 0.0001)
    p.arc(10.0001, 10.0001, 123.456, 0, math.pi - 0.0001)
    assert str(p) == precision(str(p0), 1)

    p0.arc(10.0001, 10.0001, 123.456, 0, math.pi / 2, True)
    p.arc(10.0001, 10.0001, 123.456, 0, math.pi / 2, True)
    assert str(p) == precision(str(p0), 1)


def test_path_round_arc_to_limits_precision() -> None:
    p0 = path()
    p = pathRound(1)
    p0.arcTo(10.0001, 10.0001, 123.456, 456.789, 12345.6789)
    p.arcTo(10.0001, 10.0001, 123.456, 456.789, 12345.6789)
    assert str(p) == precision(str(p0), 1)


def test_path_round_quadratic_curve_to_limits_precision() -> None:
    p0 = path()
    p = pathRound(1)
    p0.quadraticCurveTo(10.0001, 10.0001, 123.456, 456.789)
    p.quadraticCurveTo(10.0001, 10.0001, 123.456, 456.789)
    assert str(p) == precision(str(p0), 1)


def test_path_round_bezier_curve_to_limits_precision() -> None:
    p0 = path()
    p = pathRound(1)
    p0.bezierCurveTo(10.0001, 10.0001, 123.456, 456.789, 0.007, 0.006)
    p.bezierCurveTo(10.0001, 10.0001, 123.456, 456.789, 0.007, 0.006)
    assert str(p) == precision(str(p0), 1)


def test_path_round_rect_limits_precision() -> None:
    p0 = path()
    p = pathRound(1)
    p0.rect(10.0001, 10.0001, 123.456, 456.789)
    p.rect(10.0001, 10.0001, 123.456, 456.789)
    assert str(p) == precision(str(p0), 1)


_RE_FLOAT = re.compile(r"\d+\.\d+")


def precision(s: str, digits: int) -> str:
    def repl(m: re.Match[str]) -> str:
        x = float(m.group(0))
        y = float(f"{x:.{digits}f}")
        if abs(y - round(y)) < 1e-6:
            return str(int(round(y)))
        return str(y)

    return _RE_FLOAT.sub(repl, s)
