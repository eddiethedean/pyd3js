from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta, ease_in_out, ease_out


def test_ease_elastic_is_out() -> None:
    assert m.easeElastic is m.easeElasticOut


def test_ease_elastic_in_table() -> None:
    assert abs(m.easeElasticIn(0.0)) == 0.0
    expected = (
        0.000978,
        -0.001466,
        -0.003421,
        0.014663,
        -0.015152,
        -0.030792,
        0.124145,
        -0.124633,
        -0.249756,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(m.easeElasticIn(i / 10), e)
    assert m.easeElasticIn(1.0) == 1.0


def test_ease_elastic_in_coerces() -> None:
    assert m.easeElasticIn(".9") == m.easeElasticIn(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeElasticIn(_V()) == m.easeElasticIn(0.9)


def test_ease_elastic_in_amplitude_period_default() -> None:
    d = m.easeElasticIn.amplitude(1).period(0.3)
    assert m.easeElasticIn(0.1) == d(0.1)
    assert m.easeElasticIn(0.2) == d(0.2)
    assert m.easeElasticIn(0.3) == d(0.3)


def test_ease_elastic_in_amplitude_clamped() -> None:
    assert m.easeElasticIn.amplitude(-1.0)(0.1) == m.easeElasticIn(0.1)
    assert m.easeElasticIn.amplitude(0.4)(0.2) == m.easeElasticIn(0.2)
    assert m.easeElasticIn.amplitude(0.8)(0.3) == m.easeElasticIn(0.3)


def test_ease_elastic_in_amplitude_period_coerces() -> None:
    e = m.easeElasticIn.amplitude("1.3").period("0.2")(".9")
    assert e == m.easeElasticIn.amplitude(1.3).period(0.2)(0.9)

    class _A:
        def valueOf(self) -> float:
            return 1.3

    class _P:
        def valueOf(self) -> float:
            return 0.2

    class _T:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeElasticIn.amplitude(_A()).period(_P())(
        _T()
    ) == m.easeElasticIn.amplitude(1.3).period(0.2)(0.9)


def test_ease_elastic_in_amplitude_13() -> None:
    f = m.easeElasticIn.amplitude(1.3)
    assert f(0.0) == 0.0
    expected = (
        0.000978,
        -0.003576,
        0.001501,
        0.014663,
        -0.036951,
        0.013510,
        0.124145,
        -0.303950,
        0.109580,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(f(i / 10), e)
    assert f(1.0) == 1.0


def test_ease_elastic_in_amplitude_15_period_1() -> None:
    f = m.easeElasticIn.amplitude(1.5).period(1)
    assert f(0.0) == 0.0
    expected = (
        0.000148,
        -0.002212,
        -0.009390,
        -0.021498,
        -0.030303,
        -0.009352,
        0.093642,
        0.342077,
        0.732374,
    )
    for i, e in enumerate(expected, start=1):
        assert_in_delta(f(i / 10), e)
    assert f(1.0) == 1.0


def test_ease_elastic_out_matches_generic() -> None:
    ref = ease_out(m.easeElasticIn)
    assert m.easeElasticOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeElasticOut(t), ref(t))
    assert m.easeElasticOut(1.0) == ref(1.0)


def test_ease_elastic_out_amplitude_period_coerces() -> None:
    e = m.easeElasticOut.amplitude("1.3").period("0.2")(".9")
    assert e == m.easeElasticOut.amplitude(1.3).period(0.2)(0.9)

    class _A:
        def valueOf(self) -> float:
            return 1.3

    class _P:
        def valueOf(self) -> float:
            return 0.2

    class _T:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeElasticOut.amplitude(_A()).period(_P())(
        _T()
    ) == m.easeElasticOut.amplitude(1.3).period(0.2)(0.9)


def test_ease_elastic_in_out_matches_generic() -> None:
    ref = ease_in_out(m.easeElasticIn)
    assert m.easeElasticInOut(0.0) == ref(0.0)
    for i in range(1, 10):
        t = i / 10
        assert_in_delta(m.easeElasticInOut(t), ref(t))
    assert m.easeElasticInOut(1.0) == ref(1.0)


def test_ease_elastic_in_out_amplitude_period_coerces() -> None:
    e = m.easeElasticInOut.amplitude("1.3").period("0.2")(".9")
    assert e == m.easeElasticInOut.amplitude(1.3).period(0.2)(0.9)

    class _A:
        def valueOf(self) -> float:
            return 1.3

    class _P:
        def valueOf(self) -> float:
            return 0.2

    class _T:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeElasticInOut.amplitude(_A()).period(_P())(
        _T()
    ) == m.easeElasticInOut.amplitude(1.3).period(0.2)(0.9)
