from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_back_is_in_out() -> None:
    assert m.easeBack is m.easeBackInOut


def test_ease_back_in() -> None:
    assert abs(m.easeBackIn(0.0)) == 0.0
    expected = (
        -0.014314,
        -0.046451,
        -0.080200,
        -0.099352,
        -0.087698,
        -0.029028,
        0.092868,
        0.294198,
        0.591172,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easeBackIn(i / 10), e)
    assert m.easeBackIn(1.0) == 1.0


def test_ease_back_in_coerces() -> None:
    assert m.easeBackIn(".9") == m.easeBackIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeBackIn(_V()) == m.easeBackIn(0.9)


def test_ease_back_out_matches_generic() -> None:
    ref = ease_out(m.easeBackIn)
    assert m.easeBackOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeBackOut(t), ref(t))
    assert m.easeBackOut(1.0) == ref(1.0)


def test_ease_back_out_coerces() -> None:
    assert m.easeBackOut(".9") == m.easeBackOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeBackOut(_V()) == m.easeBackOut(0.9)


def test_ease_back_in_out_matches_generic() -> None:
    ref = ease_in_out(m.easeBackIn)
    assert m.easeBackInOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeBackInOut(t), ref(t))
    assert m.easeBackInOut(1.0) == ref(1.0)


def test_ease_back_in_out_coerces() -> None:
    assert m.easeBackInOut(".9") == m.easeBackInOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeBackInOut(_V()) == m.easeBackInOut(0.9)


def test_back_overshoot_chain() -> None:
    b = m.easeBackIn.overshoot(2.0)
    assert b is not m.easeBackIn
    assert isinstance(b(0.5), float)

    bo = m.easeBackOut.overshoot(2.0)
    assert bo is not m.easeBackOut
    assert isinstance(bo(0.5), float)

    bio = m.easeBackInOut.overshoot(2.0)
    assert bio is not m.easeBackInOut
    assert isinstance(bio(0.5), float)
