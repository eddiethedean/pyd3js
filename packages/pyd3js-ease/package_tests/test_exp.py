from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_exp_is_in_out() -> None:
    assert m.easeExp is m.easeExpInOut


def test_ease_exp_in() -> None:
    assert m.easeExpIn(0.0) == 0.0
    expected = (
        0.000978,
        0.002933,
        0.006843,
        0.014663,
        0.030303,
        0.061584,
        0.124145,
        0.249267,
        0.499511,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easeExpIn(i / 10), e)
    assert m.easeExpIn(1.0) == 1.0


def test_ease_exp_in_coerces() -> None:
    assert m.easeExpIn(".9") == m.easeExpIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeExpIn(_V()) == m.easeExpIn(0.9)


def test_ease_exp_out_matches_generic() -> None:
    ref = ease_out(m.easeExpIn)
    for i in range(11):
        t = i / 10
        assert_in_delta(m.easeExpOut(t), ref(t))


def test_ease_exp_out_coerces() -> None:
    assert m.easeExpOut(".9") == m.easeExpOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeExpOut(_V()) == m.easeExpOut(0.9)


def test_ease_exp_in_out_matches_generic() -> None:
    ref = ease_in_out(m.easeExpIn)
    assert m.easeExpInOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeExpInOut(t), ref(t))
    assert m.easeExpInOut(1.0) == ref(1.0)


def test_ease_exp_in_out_coerces() -> None:
    assert m.easeExpInOut(".9") == m.easeExpInOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeExpInOut(_V()) == m.easeExpInOut(0.9)
