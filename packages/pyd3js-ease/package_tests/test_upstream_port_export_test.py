from __future__ import annotations

import pyd3js_ease as m


def test_public_exports_match_upstream_index_js() -> None:
    """Names exported from d3-ease `src/index.js` @ v3.0.1 (plus `__version__`)."""
    expected = {
        "__version__",
        "easeLinear",
        "easeQuad",
        "easeQuadIn",
        "easeQuadOut",
        "easeQuadInOut",
        "easeCubic",
        "easeCubicIn",
        "easeCubicOut",
        "easeCubicInOut",
        "easePoly",
        "easePolyIn",
        "easePolyOut",
        "easePolyInOut",
        "easeSin",
        "easeSinIn",
        "easeSinOut",
        "easeSinInOut",
        "easeExp",
        "easeExpIn",
        "easeExpOut",
        "easeExpInOut",
        "easeCircle",
        "easeCircleIn",
        "easeCircleOut",
        "easeCircleInOut",
        "easeBounce",
        "easeBounceIn",
        "easeBounceOut",
        "easeBounceInOut",
        "easeBack",
        "easeBackIn",
        "easeBackOut",
        "easeBackInOut",
        "easeElastic",
        "easeElasticIn",
        "easeElasticOut",
        "easeElasticInOut",
    }
    exported = set(m.__all__)
    assert expected <= exported, sorted(expected - exported)

    for name in sorted(expected):
        assert hasattr(m, name), name
        obj = getattr(m, name)
        if name == "__version__":
            assert isinstance(obj, str)
        else:
            assert callable(obj), name

    assert m.easeQuad is m.easeQuadInOut
    assert m.easeCubic is m.easeCubicInOut
    assert m.easePoly is m.easePolyInOut
    assert m.easeSin is m.easeSinInOut
    assert m.easeExp is m.easeExpInOut
    assert m.easeCircle is m.easeCircleInOut
    assert m.easeBounce is m.easeBounceOut
    assert m.easeBack is m.easeBackInOut
    assert m.easeElastic is m.easeElasticOut

    assert callable(m.easePolyIn.exponent)
    assert callable(m.easePolyOut.exponent)
    assert callable(m.easePolyInOut.exponent)
    assert callable(m.easeBackIn.overshoot)
    assert callable(m.easeBackOut.overshoot)
    assert callable(m.easeBackInOut.overshoot)
    assert callable(m.easeElasticIn.amplitude)
    assert callable(m.easeElasticIn.period)
    assert callable(m.easeElasticOut.amplitude)
    assert callable(m.easeElasticOut.period)
    assert callable(m.easeElasticInOut.amplitude)
    assert callable(m.easeElasticInOut.period)
