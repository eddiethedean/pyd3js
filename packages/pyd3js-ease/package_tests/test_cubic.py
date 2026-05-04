from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_cubic_is_in_out() -> None:
    assert m.easeCubic is m.easeCubicInOut


def test_ease_cubic_in() -> None:
    assert m.easeCubicIn(0.0) == 0.0
    expected = (0.001, 0.008, 0.027, 0.064, 0.125, 0.216, 0.343, 0.512, 0.729)
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easeCubicIn(i / 10), e)
    assert m.easeCubicIn(1.0) == 1.0


def test_ease_cubic_in_coerces() -> None:
    assert m.easeCubicIn(".9") == m.easeCubicIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeCubicIn(_V()) == m.easeCubicIn(0.9)


def test_ease_cubic_out_matches_generic() -> None:
    ref = ease_out(m.easeCubicIn)
    for i in range(11):
        t = i / 10
        assert_in_delta(m.easeCubicOut(t), ref(t))


def test_ease_cubic_out_coerces() -> None:
    assert m.easeCubicOut(".9") == m.easeCubicOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeCubicOut(_V()) == m.easeCubicOut(0.9)


def test_ease_cubic_in_out_matches_generic() -> None:
    ref = ease_in_out(m.easeCubicIn)
    for i in range(11):
        t = i / 10
        assert_in_delta(m.easeCubicInOut(t), ref(t))


def test_ease_cubic_in_out_coerces() -> None:
    assert m.easeCubicInOut(".9") == m.easeCubicInOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeCubicInOut(_V()) == m.easeCubicInOut(0.9)
