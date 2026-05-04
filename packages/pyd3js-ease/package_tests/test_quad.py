from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_quad_is_in_out() -> None:
    assert m.easeQuad is m.easeQuadInOut


def test_ease_quad_in() -> None:
    assert m.easeQuadIn(0.0) == 0.0
    expected = (0.01, 0.04, 0.09, 0.16, 0.25, 0.36, 0.49, 0.64, 0.81)
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easeQuadIn(i / 10), e)
    assert m.easeQuadIn(1.0) == 1.0


def test_ease_quad_in_coerces() -> None:
    assert m.easeQuadIn(".9") == m.easeQuadIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeQuadIn(_V()) == m.easeQuadIn(0.9)


def test_ease_quad_out_matches_generic() -> None:
    ref = ease_out(m.easeQuadIn)
    for i in range(11):
        t = i / 10
        assert_in_delta(m.easeQuadOut(t), ref(t))


def test_ease_quad_out_coerces() -> None:
    assert m.easeQuadOut(".9") == m.easeQuadOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeQuadOut(_V()) == m.easeQuadOut(0.9)


def test_ease_quad_in_out_matches_generic() -> None:
    ref = ease_in_out(m.easeQuadIn)
    for i in range(11):
        t = i / 10
        assert_in_delta(m.easeQuadInOut(t), ref(t))


def test_ease_quad_in_out_coerces() -> None:
    assert m.easeQuadInOut(".9") == m.easeQuadInOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeQuadInOut(_V()) == m.easeQuadInOut(0.9)
