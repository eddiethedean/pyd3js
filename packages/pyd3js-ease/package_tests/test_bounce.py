from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_bounce_is_out() -> None:
    assert m.easeBounce is m.easeBounceOut


def test_ease_bounce_in() -> None:
    assert m.easeBounceIn(0.0) == 0.0
    expected = (
        0.011875,
        0.060000,
        0.069375,
        0.227500,
        0.234375,
        0.090000,
        0.319375,
        0.697500,
        0.924375,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easeBounceIn(i / 10), e)
    assert m.easeBounceIn(1.0) == 1.0


def test_ease_bounce_in_coerces() -> None:
    assert m.easeBounceIn(".9") == m.easeBounceIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeBounceIn(_V()) == m.easeBounceIn(0.9)


def test_ease_bounce_out_matches_generic() -> None:
    ref = ease_out(m.easeBounceIn)
    assert m.easeBounceOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeBounceOut(t), ref(t))
    assert m.easeBounceOut(1.0) == ref(1.0)


def test_ease_bounce_out_coerces() -> None:
    assert m.easeBounceOut(".9") == m.easeBounceOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeBounceOut(_V()) == m.easeBounceOut(0.9)


def test_ease_bounce_in_out_matches_generic() -> None:
    ref = ease_in_out(m.easeBounceIn)
    assert m.easeBounceInOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeBounceInOut(t), ref(t))
    assert m.easeBounceInOut(1.0) == ref(1.0)


def test_ease_bounce_in_out_coerces() -> None:
    assert m.easeBounceInOut(".9") == m.easeBounceInOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeBounceInOut(_V()) == m.easeBounceInOut(0.9)
