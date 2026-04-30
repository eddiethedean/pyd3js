"""Port of upstream `test/rgb-test.js`."""

from __future__ import annotations



from pyd3js_color.color import Color, Rgb, hsl, rgb

from asserts import assert_rgb_approx_equal, assert_rgb_equal


class _TestColor(Color):
    """Minimal external colorspace (upstream `TestColor` prototype test)."""

    def rgb(self) -> Rgb:
        return rgb(12, 34, 56, 0.4)


def test_rgb_is_rgb_and_color() -> None:
    c = rgb(70, 130, 180)
    assert isinstance(c, Rgb)
    assert isinstance(c, Color)


def test_rgb_channels() -> None:
    assert_rgb_approx_equal(rgb("#abc"), 170, 187, 204, 1)
    assert_rgb_approx_equal(rgb("rgba(170, 187, 204, 0.4)"), 170, 187, 204, 0.4)


def test_rgb_string_formats() -> None:
    assert str(rgb("#abcdef")) == "rgb(171, 205, 239)"
    assert str(rgb("moccasin")) == "rgb(255, 228, 181)"
    assert str(rgb("hsl(60, 100%, 20%)")) == "rgb(102, 102, 0)"
    assert str(rgb("rgb(12, 34, 56)")) == "rgb(12, 34, 56)"
    assert str(rgb(rgb(12, 34, 56))) == "rgb(12, 34, 56)"
    assert str(rgb(hsl(60, 1, 0.2))) == "rgb(102, 102, 0)"
    assert str(rgb("rgba(12, 34, 56, 0.4)")) == "rgba(12, 34, 56, 0.4)"
    assert str(rgb("rgba(12%, 34%, 56%, 0.4)")) == "rgba(31, 87, 143, 0.4)"
    assert str(rgb("hsla(60, 100%, 20%, 0.4)")) == "rgba(102, 102, 0, 0.4)"


def test_format_rgb_hsl_hex() -> None:
    assert rgb("#abcdef").formatRgb() == "rgb(171, 205, 239)"
    assert rgb("hsl(60, 100%, 20%)").formatRgb() == "rgb(102, 102, 0)"
    assert rgb("rgba(12%, 34%, 56%, 0.4)").formatRgb() == "rgba(31, 87, 143, 0.4)"
    assert rgb("hsla(60, 100%, 20%, 0.4)").formatRgb() == "rgba(102, 102, 0, 0.4)"

    assert rgb("#abcdef").formatHsl() == "hsl(210, 68%, 80.3921568627451%)"
    assert rgb("hsl(60, 100%, 20%)").formatHsl() == "hsl(60, 100%, 20%)"
    assert rgb("rgba(12%, 34%, 56%, 0.4)").formatHsl() == (
        "hsla(210, 64.70588235294117%, 34%, 0.4)"
    )
    assert rgb("hsla(60, 100%, 20%, 0.4)").formatHsl() == "hsla(60, 100%, 20%, 0.4)"

    assert rgb("#abcdef").formatHex() == "#abcdef"
    assert rgb("hsl(60, 100%, 20%)").formatHex() == "#666600"
    assert rgb("rgba(12%, 34%, 56%, 0.4)").formatHex() == "#1f578f"
    assert rgb("hsla(60, 100%, 20%, 0.4)").formatHex() == "#666600"

    assert rgb("#abcdef").formatHex8() == "#abcdefff"
    assert rgb("hsl(60, 100%, 20%)").formatHex8() == "#666600ff"
    assert rgb("rgba(12%, 34%, 56%, 0.4)").formatHex8() == "#1f578f66"
    assert rgb("hsla(60, 100%, 20%, 0.4)").formatHex8() == "#66660066"


def test_hex_alias() -> None:
    c = rgb("#abc")
    assert c.hex == c.formatHex()


def test_to_string_mutations() -> None:
    c = rgb("#abc")
    c.r += 1
    c.g += 1
    c.b += 1
    c.opacity = 0.5
    assert str(c) == "rgba(171, 188, 205, 0.5)"


def test_to_string_nan_channels() -> None:
    assert str(rgb("invalid")) == "rgb(0, 0, 0)"
    assert str(rgb(float("nan"), 12, 34)) == "rgb(0, 12, 34)"


def test_nan_opacity_prints_as_rgb_without_alpha() -> None:
    c = rgb("#abc")
    c.r += 1
    c.g += 1
    c.b += 1
    c.opacity = float("nan")
    assert str(c) == "rgb(171, 188, 205)"


def test_to_string_clamp() -> None:
    assert str(rgb(-1, 2, 3)) == "rgb(0, 2, 3)"
    assert str(rgb(2, -1, 3)) == "rgb(2, 0, 3)"
    assert str(rgb(2, 3, -1)) == "rgb(2, 3, 0)"
    assert str(rgb(2, 3, -1, -0.2)) == "rgba(2, 3, 0, 0)"
    assert str(rgb(2, 3, -1, 1.2)) == "rgb(2, 3, 0)"


def test_rounding_display() -> None:
    assert str(rgb(0.5, 2.0, 3.0)) == "rgb(1, 2, 3)"
    assert str(rgb(2.0, 0.5, 3.0)) == "rgb(2, 1, 3)"
    assert str(rgb(2.0, 3.0, 0.5)) == "rgb(2, 3, 1)"


def test_raw_channels_unclamped() -> None:
    assert_rgb_equal(rgb(1.2, 2.6, 42.9), 1.2, 2.6, 42.9, 1)
    assert_rgb_approx_equal(rgb(-10, -20, -30), -10, -20, -30, 1)
    assert_rgb_approx_equal(rgb(300, 400, 500), 300, 400, 500, 1)


def test_clamp_method() -> None:
    assert_rgb_approx_equal(rgb(-10, -20, -30).clamp(), 0, 0, 0, 1)
    assert_rgb_approx_equal(rgb(10.5, 20.5, 30.5).clamp(), 11, 21, 31, 1)
    assert_rgb_approx_equal(rgb(300, 400, 500).clamp(), 255, 255, 255, 1)
    assert rgb(10.5, 20.5, 30.5, -1).clamp().opacity == 0
    assert rgb(10.5, 20.5, 30.5, 0.5).clamp().opacity == 0.5
    assert rgb(10.5, 20.5, 30.5, 2).clamp().opacity == 1
    assert rgb(10.5, 20.5, 30.5, float("nan")).clamp().opacity == 1


def test_opacity_not_clamped_on_construct() -> None:
    assert_rgb_approx_equal(rgb(-10, -20, -30, -0.2), -10, -20, -30, -0.2)
    assert_rgb_approx_equal(rgb(300, 400, 500, 1.2), 300, 400, 500, 1.2)


def test_coerce_strings_and_null() -> None:
    assert_rgb_approx_equal(rgb("12", "34", "56"), 12, 34, 56, 1)
    assert_rgb_approx_equal(rgb(None, None, None), 0, 0, 0, 1)


def test_coerce_opacity_string() -> None:
    assert_rgb_equal(rgb(-10, -20, -30, "-0.2"), -10, -20, -30, -0.2)
    assert_rgb_equal(rgb(300, 400, 500, "1.2"), 300, 400, 500, 1.2)


def test_undefined_like_channels() -> None:
    nan = float("nan")
    assert_rgb_approx_equal(rgb(nan, nan, float("nan")), nan, nan, nan, 1)
    assert_rgb_approx_equal(rgb(nan, 42, 56), nan, 42, 56, 1)
    assert_rgb_approx_equal(rgb(42, nan, 56), 42, nan, 56, 1)
    assert_rgb_approx_equal(rgb(42, 56, nan), 42, 56, nan, 1)


def test_nullish_opacity_defaults() -> None:
    assert_rgb_approx_equal(rgb(10, 20, 30, None), 10, 20, 30, 1)


def test_rgb_parse_formats() -> None:
    assert_rgb_approx_equal(rgb("#abcdef"), 171, 205, 239, 1)
    assert_rgb_approx_equal(rgb("rgb(12, 34, 56)"), 12, 34, 56, 1)
    assert_rgb_approx_equal(rgb("rgb(12%, 34%, 56%)"), 31, 87, 143, 1)
    assert_rgb_approx_equal(rgb("hsl(60,100%,20%)"), 102, 102, 0, 1)
    assert_rgb_approx_equal(rgb("aliceblue"), 240, 248, 255, 1)
    assert_rgb_approx_equal(rgb("hsla(60,100%,20%,0.4)"), 102, 102, 0, 0.4)


def test_alpha_zero_rgba() -> None:
    assert_rgb_approx_equal(rgb("rgba(12,34,45,0)"), float("nan"), float("nan"), float("nan"), 0)
    assert_rgb_approx_equal(
        rgb("rgba(12,34,45,-0.1)"), float("nan"), float("nan"), float("nan"), -0.1
    )


def test_invalid_format() -> None:
    nan = float("nan")
    assert_rgb_approx_equal(rgb("invalid"), nan, nan, nan, nan)


def test_rgb_copy_semantics() -> None:
    c1 = rgb("rgba(70, 130, 180, 0.4)")
    c2 = rgb(c1)
    assert_rgb_approx_equal(c1, 70, 130, 180, 0.4)
    c1.r = c1.g = c1.b = c1.opacity = 0
    assert_rgb_approx_equal(c1, 0, 0, 0, 0)
    assert_rgb_approx_equal(c2, 70, 130, 180, 0.4)


def test_rgb_from_hsl() -> None:
    assert_rgb_approx_equal(rgb(hsl(0, 1, 0.5)), 255, 0, 0, 1)
    assert_rgb_approx_equal(rgb(hsl(0, 1, 0.5, 0.4)), 255, 0, 0, 0.4)


def test_rgb_from_custom_color() -> None:
    assert_rgb_approx_equal(rgb(_TestColor()), 12, 34, 56, 0.4)


def test_displayable() -> None:
    assert rgb("white").displayable() is True
    assert rgb("red").displayable() is True
    assert rgb("black").displayable() is True
    assert rgb("invalid").displayable() is False
    assert rgb(-1, 0, 0).displayable() is False
    assert rgb(0, -1, 0).displayable() is False
    assert rgb(0, 0, -1).displayable() is False
    assert rgb(256, 0, 0).displayable() is False
    assert rgb(0, 256, 0).displayable() is False
    assert rgb(0, 0, 256).displayable() is False
    assert rgb(0, 0, 255, 0).displayable() is True
    assert rgb(0, 0, 255, 1.2).displayable() is False
    assert rgb(0, 0, 255, -0.2).displayable() is False


def test_brighter_darker() -> None:
    c = rgb("rgba(165, 42, 42, 0.4)")
    assert_rgb_approx_equal(c.brighter(0.5), 197, 50, 50, 0.4)
    assert_rgb_approx_equal(c.brighter(1), 236, 60, 60, 0.4)
    assert_rgb_approx_equal(c.brighter(2), 337, 86, 86, 0.4)

    c1 = rgb("rgba(70, 130, 180, 0.4)")
    c2 = c1.brighter(1)
    assert_rgb_approx_equal(c1, 70, 130, 180, 0.4)
    assert_rgb_approx_equal(c2, 100, 186, 257, 0.4)

    c3 = c1.brighter()
    c4 = c1.brighter(1)
    assert_rgb_approx_equal(c3, c4.r, c4.g, c4.b, 0.4)

    c5 = c1.brighter(1.5)
    c6 = c1.darker(-1.5)
    assert_rgb_approx_equal(c5, c6.r, c6.g, c6.b, 0.4)

    b1 = rgb("black")
    b2 = b1.brighter(1)
    assert_rgb_approx_equal(b1, 0, 0, 0, 1)
    assert_rgb_approx_equal(b2, 0, 0, 0, 1)

    d = rgb("rgba(165, 42, 42, 0.4)")
    assert_rgb_approx_equal(d.darker(0.5), 138, 35, 35, 0.4)
    assert_rgb_approx_equal(d.darker(1), 115, 29, 29, 0.4)
    assert_rgb_approx_equal(d.darker(2), 81, 21, 21, 0.4)

    e1 = rgb("rgba(70, 130, 180, 0.4)")
    e2 = e1.darker(1)
    assert_rgb_approx_equal(e1, 70, 130, 180, 0.4)
    assert_rgb_approx_equal(e2, 49, 91, 126, 0.4)

    e3 = e1.darker()
    e4 = e1.darker(1)
    assert_rgb_approx_equal(e3, e4.r, e4.g, e4.b, 0.4)

    e5 = e1.darker(1.5)
    e6 = e1.brighter(-1.5)
    assert_rgb_approx_equal(e5, e6.r, e6.g, e6.b, 0.4)


def test_rgb_identity() -> None:
    c = rgb(70, 130, 180)
    assert c.rgb() is c


def test_copy_channels() -> None:
    c = rgb(70, 130, 180)
    assert isinstance(c.copy(), Rgb)
    assert str(c.copy()) == "rgb(70, 130, 180)"
    assert str(c.copy(opacity=0.2)) == "rgba(70, 130, 180, 0.2)"
    assert str(c.copy(r=20)) == "rgb(20, 130, 180)"
    assert str(c.copy(r=20, g=40)) == "rgb(20, 40, 180)"
