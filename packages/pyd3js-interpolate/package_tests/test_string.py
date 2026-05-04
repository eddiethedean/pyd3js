from __future__ import annotations

from pyd3js_interpolate import interpolateString


def test_interpolate_string() -> None:
    assert interpolateString(" 10/20 30", "50/10 100 ")(0.2) == "18/18 44 "
    assert interpolateString(" 10/20 30", "50/10 100 ")(0.4) == "26/16 58 "

    class A:
        def __str__(self) -> str:
            return "2px"

    class B:
        def __str__(self) -> str:
            return "12px"

    assert interpolateString(A(), B())(0.25) == "4.5px"

    assert interpolateString(" 10/20 30", "50/10 foo ")(0.2) == "18/18 foo "
    assert interpolateString(" 10/20 foo", "50/10 100 ")(0.2) == "18/18 100 "
    assert interpolateString(" 10/20 100 20", "50/10 100, 20 ")(0.2) == "18/18 100, 20 "
    assert interpolateString("1.", "2.")(0.5) == "1.5"
    assert interpolateString("1e+3", "1e+4")(0.5) == "5500"
    assert interpolateString("1e-3", "1e-4")(0.5) == "0.00055"
    assert interpolateString("1.e-3", "1.e-4")(0.5) == "0.00055"
    assert interpolateString("-1.e-3", "-1.e-4")(0.5) == "-0.00055"
    assert interpolateString("+1.e-3", "+1.e-4")(0.5) == "0.00055"
    assert interpolateString(".1e-2", ".1e-3")(0.5) == "0.00055"
    assert interpolateString("foo", "bar")(0.5) == "bar"
    assert interpolateString("foo", "")(0.5) == ""
    assert interpolateString("", "bar")(0.5) == "bar"
    assert interpolateString("", "")(0.5) == ""
    assert interpolateString("top: 1000px;", "top: 1e3px;")(0.5) == "top: 1000px;"
    assert interpolateString("top: 1e3px;", "top: 1000px;")(0.5) == "top: 1000px;"
