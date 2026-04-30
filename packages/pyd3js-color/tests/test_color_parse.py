"""Port of upstream `test/color-test.js`."""

from __future__ import annotations

import math

import pytest

from pyd3js_color import color
from pyd3js_color.color import Hsl, Rgb

from asserts import assert_hsl_equal, assert_rgb_approx_equal, assert_rgb_equal


def test_color_names_and_transparent() -> None:
    assert_rgb_approx_equal(color("moccasin"), 255, 228, 181, 1)
    assert_rgb_approx_equal(color("aliceblue"), 240, 248, 255, 1)
    assert_rgb_approx_equal(color("yellow"), 255, 255, 0, 1)
    assert_rgb_approx_equal(color("rebeccapurple"), 102, 51, 153, 1)
    c = color("transparent")
    assert isinstance(c, Rgb)
    assert math.isnan(c.r) and math.isnan(c.g) and math.isnan(c.b)
    assert c.opacity == 0


def test_hex_variants() -> None:
    assert_rgb_approx_equal(color("#abcdef"), 171, 205, 239, 1)
    assert_rgb_approx_equal(color("#abc"), 170, 187, 204, 1)
    assert color("#abcdef3") is None
    assert_rgb_approx_equal(color("#abcdef33"), 171, 205, 239, 0.2)
    assert_rgb_approx_equal(color("#abc3"), 170, 187, 204, 0.2)


def test_rgb_rgba_integer_percent() -> None:
    assert_rgb_approx_equal(color("rgb(12,34,56)"), 12, 34, 56, 1)
    assert_rgb_approx_equal(color("rgba(12,34,56,0.4)"), 12, 34, 56, 0.4)
    assert_rgb_approx_equal(color("rgb(12%,34%,56%)"), 31, 87, 143, 1)
    assert_rgb_equal(color("rgb(100%,100%,100%)"), 255, 255, 255, 1)
    assert_rgb_approx_equal(color("rgba(12%,34%,56%,0.4)"), 31, 87, 143, 0.4)
    assert_rgb_equal(color("rgba(100%,100%,100%,0.4)"), 255, 255, 255, 0.4)


def test_hsl_hsla_parse() -> None:
    c = color("hsl(60,100%,20%)")
    assert isinstance(c, Hsl)
    assert_hsl_equal(c, 60, 1, 0.2, 1)
    c2 = color("hsla(60,100%,20%,0.4)")
    assert isinstance(c2, Hsl)
    assert_hsl_equal(c2, 60, 1, 0.2, 0.4)


def test_whitespace() -> None:
    assert_rgb_approx_equal(color(" aliceblue\t\n"), 240, 248, 255, 1)
    assert_rgb_approx_equal(color(" #abc\t\n"), 170, 187, 204, 1)
    assert_rgb_approx_equal(color(" #aabbcc\t\n"), 170, 187, 204, 1)
    assert_rgb_approx_equal(color(" rgb(120,30,50)\t\n"), 120, 30, 50, 1)
    assert_hsl_equal(color(" hsl(120,30%,50%)\t\n"), 120, 0.3, 0.5, 1)


def test_whitespace_between_numbers() -> None:
    assert_rgb_approx_equal(color(" rgb( 120 , 30 , 50 ) "), 120, 30, 50, 1)
    assert_hsl_equal(color(" hsl( 120 , 30% , 50% ) "), 120, 0.3, 0.5, 1)
    assert_rgb_approx_equal(color(" rgba( 12 , 34 , 56 , 0.4 ) "), 12, 34, 56, 0.4)
    assert_rgb_approx_equal(color(" rgba( 12% , 34% , 56% , 0.4 ) "), 31, 87, 143, 0.4)
    assert_hsl_equal(color(" hsla( 60 , 100% , 20% , 0.4 ) "), 60, 1, 0.2, 0.4)


def test_number_signs() -> None:
    assert_rgb_approx_equal(color("rgb(+120,+30,+50)"), 120, 30, 50, 1)
    assert_hsl_equal(color("hsl(+120,+30%,+50%)"), 120, 0.3, 0.5, 1)
    assert_rgb_approx_equal(color("rgb(-120,-30,-50)"), -120, -30, -50, 1)
    assert_hsl_equal(color("hsl(-120,-30%,-50%)"), float("nan"), float("nan"), -0.5, 1)
    assert_rgb_approx_equal(color("rgba(12,34,56,+0.4)"), 12, 34, 56, 0.4)
    c = color("rgba(12,34,56,-0.4)")
    assert isinstance(c, Rgb)
    assert math.isnan(c.r) and math.isnan(c.g) and math.isnan(c.b)
    assert c.opacity == -0.4
    assert_rgb_approx_equal(color("rgba(12%,34%,56%,+0.4)"), 31, 87, 143, 0.4)
    c2 = color("rgba(12%,34%,56%,-0.4)")
    assert isinstance(c2, Rgb)
    assert math.isnan(c2.r) and math.isnan(c2.g) and math.isnan(c2.b)
    assert_hsl_equal(color("hsla(60,100%,20%,+0.4)"), 60, 1, 0.2, 0.4)
    c3 = color("hsla(60,100%,20%,-0.4)")
    assert isinstance(c3, Hsl)
    assert math.isnan(c3.h) and math.isnan(c3.s) and math.isnan(c3.l)
    assert c3.opacity == -0.4


def test_decimals_and_exponent() -> None:
    assert_rgb_approx_equal(color("rgb(20.0%,30.4%,51.2%)"), 51, 78, 131, 1)
    assert_hsl_equal(color("hsl(20.0,30.4%,51.2%)"), 20, 0.304, 0.512, 1)
    assert_hsl_equal(color("hsl(.9,.3%,.5%)"), 0.9, 0.003, 0.005, 1)
    assert_hsl_equal(color("hsla(.9,.3%,.5%,.5)"), 0.9, 0.003, 0.005, 0.5)
    assert_rgb_approx_equal(color("rgb(.1%,.2%,.3%)"), 0, 1, 1, 1)
    assert_rgb_approx_equal(color("rgba(120,30,50,.5)"), 120, 30, 50, 0.5)
    assert_hsl_equal(color("hsl(1e1,2e1%,3e1%)"), 10, 0.2, 0.3, 1)
    assert_hsl_equal(color("hsla(9e-1,3e-1%,5e-1%,5e-1)"), 0.9, 0.003, 0.005, 0.5)
    assert_rgb_approx_equal(color("rgb(1e-1%,2e-1%,3e-1%)"), 0, 1, 1, 1)
    assert_rgb_approx_equal(color("rgba(120,30,50,1e-1)"), 120, 30, 50, 0.1)


@pytest.mark.parametrize(
    "s",
    [
        "rgb(120.5,30,50)",
        "rgb(120.,30,50)",
        "rgb(120.%,30%,50%)",
        "rgba(120,30,50,1.)",
        "rgba(12%,30%,50%,1.)",
        "hsla(60,100%,20%,1.)",
    ],
)
def test_invalid_decimal_rules(s: str) -> None:
    assert color(s) is None


def test_invalid_names_and_formats() -> None:
    assert color("bostock") is None
    assert color("rgb (120,30,50)") is None
    assert color("hsl (120,30%,50%)") is None
    assert color("invalid") is None
    assert color("hasOwnProperty") is None
    assert color("__proto__") is None
    assert color("#ab") is None


def test_achromatic() -> None:
    assert_rgb_approx_equal(color("rgba(0,0,0,0)"), float("nan"), float("nan"), float("nan"), 0)
    assert_rgb_approx_equal(color("#0000"), float("nan"), float("nan"), float("nan"), 0)
    assert_rgb_approx_equal(color("#00000000"), float("nan"), float("nan"), float("nan"), 0)


def test_case_insensitive() -> None:
    assert_rgb_approx_equal(color("aLiCeBlUE"), 240, 248, 255, 1)
    c = color("transPARENT")
    assert isinstance(c, Rgb)
    assert math.isnan(c.r)
    assert_rgb_approx_equal(color(" #aBc\t\n"), 170, 187, 204, 1)
    assert_rgb_approx_equal(color(" rGB(120,30,50)\t\n"), 120, 30, 50, 1)
    assert_hsl_equal(color(" HSl(120,30%,50%)\t\n"), 120, 0.3, 0.5, 1)


def test_hex_alias() -> None:
    c = color("rgba(12%,34%,56%,0.4)")
    assert c is not None
    assert c.hex == "#1f578f"
