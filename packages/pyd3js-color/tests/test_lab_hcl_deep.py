"""Additional LAB/HCL behavioral tests adapted from upstream `lab-test.js` / `hcl-test.js`."""

from __future__ import annotations

import math

from pyd3js_color.color import Color, Hsl, hsl, rgb
from pyd3js_color.cubehelix import Cubehelix
from pyd3js_color.lab import Lab, hcl, lab, lch

from asserts import assert_hcl_equal, assert_lab_equal, assert_rgb_approx_equal


class _Tc(Color):
    def rgb(self):
        return rgb(12, 34, 56, 0.4)


def test_lab_instance_and_parse_numbers() -> None:
    c = lab(120, 40, 50)
    assert isinstance(c, Lab)
    assert isinstance(c, Color)

    assert_lab_equal(
        lab("rgba(170, 187, 204, 0.4)"),
        74.96879980931759,
        -3.398998724348956,
        -10.696507207853333,
        0.4,
    )


def test_lab_strings_match_rgb() -> None:
    assert str(lab("#abcdef")) == "rgb(171, 205, 239)"
    assert str(lab("moccasin")) == "rgb(255, 228, 181)"
    assert str(lab("hsl(60, 100%, 20%)")) == "rgb(102, 102, 0)"
    assert str(lab("hsla(60, 100%, 20%, 0.4)")) == "rgba(102, 102, 0, 0.4)"
    assert str(lab("rgb(12, 34, 56)")) == "rgb(12, 34, 56)"
    assert str(lab(rgb(12, 34, 56))) == "rgb(12, 34, 56)"
    assert str(lab(hsl(60, 1, 0.2))) == "rgb(102, 102, 0)"


def test_lab_mutations_and_invalid() -> None:
    c = lab("#abc")
    c.l += 10
    c.a -= 10
    c.b += 10
    c.opacity = 0.4
    assert str(c) == "rgba(184, 220, 213, 0.4)"

    assert str(lab("invalid")) == "rgb(0, 0, 0)"
    assert str(lab(float("nan"), 0, 0)) == "rgb(0, 0, 0)"
    assert str(lab(50, float("nan"), 0)) == "rgb(119, 119, 119)"

    c2 = lab("#abc")
    c2.opacity = float("nan")
    assert str(c2) == "rgb(170, 187, 204)"


def test_lab_constructor_channels() -> None:
    assert_lab_equal(lab(-10, 1, 2), -10, 1, 2, 1)
    assert_lab_equal(lab(50, 10, 20, -0.2), 50, 10, 20, -0.2)
    assert_lab_equal(lab("50", "4", "-5"), 50, 4, -5, 1)
    assert_lab_equal(lab(50, 4, -5, "0.2"), 50, 4, -5, 0.2)


def test_lab_parse_formats() -> None:
    assert_lab_equal(
        lab("#abcdef"),
        80.77135418262527,
        -5.957098328496224,
        -20.785782794739237,
        1,
    )
    assert_lab_equal(
        lab("invalid"), float("nan"), float("nan"), float("nan"), float("nan")
    )


def test_lab_copy_and_roundtrips() -> None:
    c1 = lab(50, 4, -5, 0.4)
    c2 = lab(c1)
    assert_lab_equal(c1, 50, 4, -5, 0.4)
    c1.l = c1.a = c1.b = c1.opacity = 0
    assert_lab_equal(c1, 0, 0, 0, 0)
    assert_lab_equal(c2, 50, 4, -5, 0.4)

    assert_lab_equal(lab(hcl(lab(0, 10, 0))), 0, 10, 0, 1)
    assert_lab_equal(
        lab(rgb(255, 0, 0, 0.4)),
        54.29173376861782,
        80.8124553179771,
        69.88504032350531,
        0.4,
    )
    assert_lab_equal(
        lab(_Tc()), 12.404844123471648, -2.159950219712034, -17.168132391132946, 0.4
    )


def test_lab_brighter_darker() -> None:
    c = lab("rgba(165, 42, 42, 0.4)")
    assert_lab_equal(
        c.brighter(0.5), 47.149667346714935, 50.388769337115, 31.834059255569358, 0.4
    )
    assert_lab_equal(
        c.brighter(1), 56.149667346714935, 50.388769337115, 31.834059255569358, 0.4
    )
    assert_lab_equal(
        c.darker(1), 20.149667346714935, 50.388769337115, 31.834059255569358, 0.4
    )

    c1 = lab("rgba(70, 130, 180, 0.4)")
    c2 = c1.brighter(1)
    assert_lab_equal(
        c1, 51.98624890550498, -8.362792037014344, -32.832699449697685, 0.4
    )
    assert_lab_equal(
        c2, 69.98624890550498, -8.362792037014344, -32.832699449697685, 0.4
    )

    c3 = c1.brighter()
    c4 = c1.brighter(1)
    assert_lab_equal(c3, c4.l, c4.a, c4.b, 0.4)

    c5 = lab(50, 4, -5, 0.4)
    assert_rgb_approx_equal(c5.rgb(), 123, 117, 128, 0.4)


def test_hcl_core() -> None:
    c = hcl(120, 40, 50)
    assert isinstance(c, Color)

    assert_hcl_equal(
        hcl("#abc"), 252.37145234745182, 11.223567114593477, 74.96879980931759, 1
    )
    assert_hcl_equal(hcl("black"), float("nan"), float("nan"), 0, 1)
    assert_hcl_equal(hcl("white"), float("nan"), float("nan"), 100, 1)

    assert str(hcl("#abcdef")) == "rgb(171, 205, 239)"

    ch = hcl("#abc")
    ch.h += 10
    ch.c += 1
    ch.l -= 1
    assert str(ch) == "rgb(170, 183, 204)"


def test_hcl_constructors_and_lch() -> None:
    assert_hcl_equal(hcl(-10, 40, 50), -10, 40, 50, 1)
    assert_hcl_equal(hcl(120, 40, 50, -0.2), 120, 40, 50, -0.2)
    assert_hcl_equal(hcl("120", "40", "50"), 120, 40, 50, 1)

    assert_hcl_equal(
        lch("#abc"), 252.37145234745182, 11.223567114593477, 74.96879980931759, 1
    )


def test_cubehelix_ops() -> None:
    c = Cubehelix(300, 0.5, 0.5, 1)
    assert isinstance(c.brighter(1), Cubehelix)
    assert isinstance(c.darker(1), Cubehelix)


def test_hsl_convert_css_string_paths() -> None:
    """Exercise `hslConvert` when `color(...)` returns an `Hsl`."""
    h = hsl("hsl(60,50%,50%)")
    assert isinstance(h, Hsl)
    assert math.isfinite(h.h)


def test_hsl_grayscale_convert() -> None:
    """Exercise achromatic branch in `hslConvert`."""
    h = hsl(rgb(128, 128, 128))
    assert math.isnan(h.h)


def test_rgb_wrong_arity() -> None:
    from pyd3js_color.color import rgb as rgb_fn

    r = rgb_fn()
    assert math.isnan(r.r) and math.isnan(r.g)
    r2 = rgb_fn(1, 2)
    assert math.isnan(r2.r)


def test_hsl_wrong_arity() -> None:
    from pyd3js_color.color import hsl as hsl_fn

    h = hsl_fn()
    assert math.isnan(h.h)
