"""Ensure package surface matches d3-contour (`src/index.js`: two named exports only)."""

from __future__ import annotations

import pyd3js_contour


def test_named_exports_match_upstream_index() -> None:
    assert set(pyd3js_contour.__all__) == {"contours", "contourDensity", "__version__"}
    assert pyd3js_contour.contours is not None
    assert pyd3js_contour.contourDensity is not None


def test_contours_generator_chain_matches_js() -> None:
    c = pyd3js_contour.contours()
    assert callable(c)
    assert c.size([2, 2]) is c
    assert c.size() == [2, 2]
    assert callable(c.thresholds())
    assert callable(c.smooth(False))
    assert c.smooth() is False
    assert hasattr(c, "contour")


def test_contour_density_generator_chain_matches_js() -> None:
    d = pyd3js_contour.contourDensity()
    assert callable(d)
    assert d.size([100, 100]) is d
    assert len(d.size()) == 2
    assert callable(d.x(lambda p: p[0]))
    assert callable(d.y(lambda p: p[1]))
    assert callable(d.weight(lambda _: 1.0))
    assert d.cellSize(4) is d
    assert isinstance(d.cellSize(), int)
    assert d.bandwidth(10.0) is d
    assert isinstance(d.bandwidth(), float)
    cc = d.contours([[10.0, 10.0]])
    assert callable(cc)
    assert hasattr(cc, "max")
