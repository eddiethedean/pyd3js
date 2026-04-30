# ruff: noqa: E741 — Parameter names mirror upstream (`l` / lightness).
"""Test helpers mirroring upstream `d3-color/test/asserts.js`."""

from __future__ import annotations

import math

from pyd3js_color.color import Hsl, Rgb
from pyd3js_color.lab import Hcl, Lab


def _ch_match(a: float, b: float, tol: float = 1e-6) -> bool:
    if math.isnan(a) and math.isnan(b):
        return True
    return b - tol <= a <= b + tol


def assert_rgb_equal(actual: object, r: float, g: float, b: float, opacity: float) -> None:
    assert isinstance(actual, Rgb)
    assert (_ch_match(actual.r, r) if math.isnan(r) else actual.r == r)
    assert (_ch_match(actual.g, g) if math.isnan(g) else actual.g == g)
    assert (_ch_match(actual.b, b) if math.isnan(b) else actual.b == b)
    assert (
        _ch_match(actual.opacity, opacity) if math.isnan(opacity) else actual.opacity == opacity
    )


def assert_rgb_approx_equal(
    actual: object, r: float, g: float, b: float, opacity: float
) -> None:
    assert isinstance(actual, Rgb)
    assert (_ch_match(actual.r, r) if math.isnan(r) else round(actual.r) == round(r))
    assert (_ch_match(actual.g, g) if math.isnan(g) else round(actual.g) == round(g))
    assert (_ch_match(actual.b, b) if math.isnan(b) else round(actual.b) == round(b))
    assert (
        _ch_match(actual.opacity, opacity)
        if math.isnan(opacity)
        else actual.opacity == opacity
    )


def assert_hsl_equal(actual: object, h: float, s: float, l: float, opacity: float) -> None:
    assert isinstance(actual, Hsl)
    assert (_ch_match(actual.h, h) if math.isnan(h) else _ch_match(actual.h, h))
    assert (_ch_match(actual.s, s) if math.isnan(s) else _ch_match(actual.s, s))
    assert (_ch_match(actual.l, l) if math.isnan(l) else _ch_match(actual.l, l))
    assert (
        _ch_match(actual.opacity, opacity)
        if math.isnan(opacity)
        else actual.opacity == opacity
    )


def assert_lab_equal(actual: object, l: float, a: float, b: float, opacity: float) -> None:
    assert isinstance(actual, Lab)
    for av, ev in (
        (actual.l, l),
        (actual.a, a),
        (actual.b, b),
        (actual.opacity, opacity),
    ):
        if math.isnan(ev):
            assert math.isnan(av)
        else:
            assert math.isclose(av, ev, rel_tol=0, abs_tol=1e-9)


def assert_hcl_equal(actual: object, h: float, c: float, l: float, opacity: float) -> None:
    assert isinstance(actual, Hcl)
    for av, ev in (
        (actual.h, h),
        (actual.c, c),
        (actual.l, l),
        (actual.opacity, opacity),
    ):
        if math.isnan(ev):
            assert math.isnan(av)
        else:
            assert math.isclose(av, ev, rel_tol=0, abs_tol=1e-9)
