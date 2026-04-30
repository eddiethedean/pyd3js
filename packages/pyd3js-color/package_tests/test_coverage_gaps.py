"""Targeted tests for remaining branches (line coverage)."""

from __future__ import annotations

import math

import pytest

from pyd3js_color.color import (
    Color,
    Hsl,
    Rgb,
    _hsla,
    _js_number_str,
    _unary_plus,
    color,
    hsl,
    rgb,
)
from pyd3js_color.cubehelix import cubehelix
from pyd3js_color.lab import Hcl, Lab, hcl, hclConvert, lab, lch


def test_hsl_convert_green_and_blue_max_paths() -> None:
    """Cover `hslConvert` hue branches when G or B is the max channel."""
    hg = hsl(rgb(0, 255, 0))
    assert hg.h == pytest.approx(120.0)

    hb = hsl(rgb(0, 0, 255))
    assert hb.h == pytest.approx(240.0)


def test_color_accepts_color_instance() -> None:
    base = rgb("#abc")
    out = color(base)
    assert out is not None
    assert out.formatRgb() == base.formatRgb()


def test_hcl_brighter_darker_and_degrees_paths() -> None:
    c = hcl(120, 40, 50, 1)
    assert isinstance(c.brighter(), type(c))
    assert isinstance(c.darker(2), type(c))


def test_lab_wrong_arity() -> None:
    x = lab()
    assert math.isnan(x.l)


def test_hcl_wrong_arity() -> None:
    x = hcl()
    assert math.isnan(x.h)


def test_lch_wrong_arity() -> None:
    x = lch()
    assert math.isnan(x.h)


def test_hcl_gray_axis_chroma_rule() -> None:
    """Cover achromatic LAB conversion rules inside `hclConvert`."""
    o = hclConvert(Lab(50, 0, 0, 1))
    assert math.isnan(o.h)
    assert o.c == 0


def test_cubehelix_chain() -> None:
    c = cubehelix(rgb("orange"))
    assert isinstance(c.brighter(0.5), type(c))
    assert isinstance(c.darker(), type(c))
    assert isinstance(c.rgb(), Rgb)

    ch = cubehelix(300, 0.5, 0.5, 1)
    assert isinstance(ch.rgb(), Rgb)

    c2 = cubehelix(100, 0.2, 0.6, 1)
    assert cubehelix(c2).h == c2.h

    assert math.isnan(cubehelix().h)


def test_hcl_convert_copy_branch() -> None:
    c = hcl("#abc")
    assert math.isclose(hclConvert(c).h, c.h, abs_tol=1e-9)


def test_hcl_nan_hue_rgb_path() -> None:
    x = Hcl(float("nan"), 10, 50, 1)
    assert isinstance(x.rgb(), Rgb)


def test_unary_plus_bool_channels() -> None:
    r = rgb(True, False, True)
    assert r.r == 1.0 and r.g == 0.0 and r.b == 1.0


def test_unary_plus_string_edges() -> None:
    assert math.isnan(_unary_plus(""))
    assert math.isnan(_unary_plus("not-a-number"))


def test_js_number_str_special_floats() -> None:
    assert _js_number_str(float("nan")) == "NaN"
    assert _js_number_str(float("inf")) == "Infinity"
    assert _js_number_str(float("-inf")) == "-Infinity"
    assert _js_number_str(1e100)  # scientific notation branch


def test_hsl_brighter_darker_clamp_displayable() -> None:
    h = hsl(60, 0.5, 0.5)
    assert isinstance(h.brighter(1), Hsl)
    assert isinstance(h.darker(0.5), Hsl)
    assert isinstance(h.clamp(), Hsl)
    assert h.displayable()


def test_cubehelix_black_and_three_args() -> None:
    z = cubehelix(rgb(0, 0, 0))
    assert math.isnan(z.s)
    t = cubehelix(200, 0.4, 0.55, 1)
    assert isinstance(t.rgb(), Rgb)
    assert isinstance(cubehelix(15, 0.2, 0.7), type(t))


def test_color_base_methods_delegate_or_raise() -> None:
    with pytest.raises(NotImplementedError):
        Color().rgb()
    assert isinstance(lab("tomato").displayable(), bool)
    assert lab("#abc").formatHex().startswith("#")
    assert len(lab("#abc").formatHex8()) == 9


def test_hue_norm_negative() -> None:
    assert isinstance(hsl(-30, 0.5, 0.5).rgb(), Rgb)


def test_hsl_convert_identity_and_none() -> None:
    x = hsl(60, 0.5, 0.5)
    assert hsl(x).h == x.h
    assert math.isnan(hsl(None).h)


def test_hsla_zero_saturation_branch() -> None:
    o = _hsla(60.0, 0.0, 0.5, 1.0)
    assert math.isnan(o.h) and o.s == 0.0


def test_non_coercible_unary_plus() -> None:
    assert math.isnan(_unary_plus(object()))
