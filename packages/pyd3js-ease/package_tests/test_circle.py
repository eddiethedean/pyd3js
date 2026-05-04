from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_circle_is_in_out() -> None:
    assert m.easeCircle is m.easeCircleInOut


def test_ease_circle_in() -> None:
    assert m.easeCircleIn(0.0) == 0.0
    expected = (
        0.005013,
        0.020204,
        0.046061,
        0.083485,
        0.133975,
        0.200000,
        0.285857,
        0.400000,
        0.564110,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easeCircleIn(i / 10), e)
    assert m.easeCircleIn(1.0) == 1.0


def test_ease_circle_in_coerces() -> None:
    assert m.easeCircleIn(".9") == m.easeCircleIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeCircleIn(_V()) == m.easeCircleIn(0.9)


def test_ease_circle_out_matches_generic() -> None:
    ref = ease_out(m.easeCircleIn)
    assert m.easeCircleOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeCircleOut(t), ref(t))
    assert m.easeCircleOut(1.0) == ref(1.0)


def test_ease_circle_out_coerces() -> None:
    assert m.easeCircleOut(".9") == m.easeCircleOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeCircleOut(_V()) == m.easeCircleOut(0.9)


def test_ease_circle_in_out_matches_generic() -> None:
    ref = ease_in_out(m.easeCircleIn)
    assert m.easeCircleInOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeCircleInOut(t), ref(t))
    assert m.easeCircleInOut(1.0) == ref(1.0)


def test_ease_circle_in_out_coerces() -> None:
    assert m.easeCircleInOut(".9") == m.easeCircleInOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeCircleInOut(_V()) == m.easeCircleInOut(0.9)
