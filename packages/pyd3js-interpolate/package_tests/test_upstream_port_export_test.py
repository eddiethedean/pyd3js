from __future__ import annotations

import pyd3js_interpolate as m


def test_public_exports_match_upstream_inventory() -> None:
    expected = {
        "interpolate",
        "interpolateArray",
        "interpolateBasis",
        "interpolateBasisClosed",
        "interpolateDate",
        "interpolateDiscrete",
        "interpolateHue",
        "interpolateNumber",
        "interpolateNumberArray",
        "interpolateObject",
        "interpolateRound",
        "interpolateString",
        "interpolateTransformCss",
        "interpolateTransformSvg",
        "interpolateZoom",
        "interpolateRgb",
        "interpolateRgbBasis",
        "interpolateRgbBasisClosed",
        "interpolateHsl",
        "interpolateHslLong",
        "interpolateLab",
        "interpolateHcl",
        "interpolateHclLong",
        "interpolateCubehelix",
        "interpolateCubehelixLong",
        "piecewise",
        "quantize",
        "isNumberArray",
    }
    for name in expected:
        assert hasattr(m, name), name
        assert callable(getattr(m, name)), name

    assert callable(m.interpolateRgb.gamma)
    assert callable(m.interpolateCubehelix.gamma)
    assert callable(m.interpolateCubehelixLong.gamma)
