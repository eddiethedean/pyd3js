from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_sin_is_in_out() -> None:
    assert m.easeSin is m.easeSinInOut


def test_ease_sin_in() -> None:
    assert m.easeSinIn(0.0) == 0.0
    expected = (
        0.012312,
        0.048943,
        0.108993,
        0.190983,
        0.292893,
        0.412215,
        0.546010,
        0.690983,
        0.843566,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easeSinIn(i / 10), e)
    assert m.easeSinIn(1.0) == 1.0


def test_ease_sin_in_coerces() -> None:
    assert m.easeSinIn(".9") == m.easeSinIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeSinIn(_V()) == m.easeSinIn(0.9)


def test_ease_sin_out_matches_generic() -> None:
    ref = ease_out(m.easeSinIn)
    for i in range(11):
        t = i / 10
        assert_in_delta(m.easeSinOut(t), ref(t))


def test_ease_sin_out_coerces() -> None:
    assert m.easeSinOut(".9") == m.easeSinOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeSinOut(_V()) == m.easeSinOut(0.9)


def test_ease_sin_in_out_matches_generic() -> None:
    ref = ease_in_out(m.easeSinIn)
    for i in range(11):
        t = i / 10
        assert_in_delta(m.easeSinInOut(t), ref(t))


def test_ease_sin_in_out_coerces() -> None:
    assert m.easeSinInOut(".9") == m.easeSinInOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeSinInOut(_V()) == m.easeSinInOut(0.9)
