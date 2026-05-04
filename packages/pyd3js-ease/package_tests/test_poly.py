from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_poly_is_in_out() -> None:
    assert m.easePoly is m.easePolyInOut


def test_ease_poly_in_default_exponent() -> None:
    assert m.easePolyIn(0.0) == 0.0
    expected = (0.001, 0.008, 0.027, 0.064, 0.125, 0.216, 0.343, 0.512, 0.729)
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easePolyIn(i / 10), e)
    assert m.easePolyIn(1.0) == 1.0


def test_ease_poly_in_coerces() -> None:
    assert m.easePolyIn(".9") == m.easePolyIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easePolyIn(_V()) == m.easePolyIn(0.9)


def test_ease_poly_in_exponent_3_same_as_default() -> None:
    assert m.easePolyIn(0.1) == m.easePolyIn.exponent(3)(0.1)
    assert m.easePolyIn(0.2) == m.easePolyIn.exponent(3)(0.2)
    assert m.easePolyIn(0.3) == m.easePolyIn.exponent(3)(0.3)


def test_ease_poly_in_exponent_coerces() -> None:
    assert m.easePolyIn.exponent("1.3")(".9") == m.easePolyIn.exponent(1.3)(0.9)

    class _E:
        def valueOf(self) -> float:
            return 1.3

    class _T:
        def valueOf(self) -> float:
            return 0.9

    assert m.easePolyIn.exponent(_E())(_T()) == m.easePolyIn.exponent(1.3)(0.9)


def test_ease_poly_in_exponent_25() -> None:
    p = m.easePolyIn.exponent(2.5)
    assert p(0.0) == 0.0
    expected = (
        0.003162,
        0.017889,
        0.049295,
        0.101193,
        0.176777,
        0.278855,
        0.409963,
        0.572433,
        0.768433,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(p(i / 10), e)
    assert p(1.0) == 1.0


def test_ease_poly_out_exponent_coerces() -> None:
    assert m.easePolyOut.exponent("1.3")(".9") == m.easePolyOut.exponent(1.3)(0.9)

    class _E:
        def valueOf(self) -> float:
            return 1.3

    class _T:
        def valueOf(self) -> float:
            return 0.9

    assert m.easePolyOut.exponent(_E())(_T()) == m.easePolyOut.exponent(1.3)(0.9)


def test_ease_poly_out_default() -> None:
    assert m.easePolyOut(0.1) == m.easePolyOut.exponent(3)(0.1)
    assert m.easePolyOut(0.2) == m.easePolyOut.exponent(3)(0.2)
    assert m.easePolyOut(0.3) == m.easePolyOut.exponent(3)(0.3)


def test_ease_poly_out_ignores_extra_positional_args() -> None:
    """Mocha: `easePolyOut(t, null)` / `easePolyOut(t, undefined)` ignore extras."""
    ref = m.easePolyOut.exponent(3)
    assert m.easePolyOut(0.1, None) == ref(0.1)
    assert m.easePolyOut(0.2, None) == ref(0.2)
    assert m.easePolyOut(0.3, None) == ref(0.3)
    assert m.easePolyOut(0.1, "ignored") == ref(0.1)
    assert m.easePolyOut(0.2, "ignored") == ref(0.2)
    assert m.easePolyOut(0.3, "ignored") == ref(0.3)


def test_ease_poly_out_exponent_25_matches_generic() -> None:
    p_in = m.easePolyIn.exponent(2.5)
    ref = ease_out(p_in)
    p = m.easePolyOut.exponent(2.5)
    for i in range(11):
        t = i / 10
        assert_in_delta(p(t), ref(t))


def test_ease_poly_in_out_exponent_coerces() -> None:
    assert m.easePolyInOut.exponent("1.3")(".9") == m.easePolyInOut.exponent(1.3)(0.9)

    class _E:
        def valueOf(self) -> float:
            return 1.3

    class _T:
        def valueOf(self) -> float:
            return 0.9

    assert m.easePolyInOut.exponent(_E())(_T()) == m.easePolyInOut.exponent(1.3)(0.9)


def test_ease_poly_in_out_default_matches_exponent_3() -> None:
    assert m.easePolyInOut(0.1) == m.easePolyInOut.exponent(3)(0.1)
    assert m.easePolyInOut(0.2) == m.easePolyInOut.exponent(3)(0.2)
    assert m.easePolyInOut(0.3) == m.easePolyInOut.exponent(3)(0.3)


def test_ease_poly_in_out_coerces() -> None:
    assert m.easePolyInOut(".9") == m.easePolyInOut(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easePolyInOut(_V()) == m.easePolyInOut(0.9)


def test_ease_poly_in_out_exponent_25_matches_generic() -> None:
    p_in = m.easePolyIn.exponent(2.5)
    ref = ease_in_out(p_in)
    p = m.easePolyInOut.exponent(2.5)
    for i in range(11):
        t = i / 10
        assert_in_delta(p(t), ref(t))
