"""Port of d3-interpolate `test/hslLong-test.js` (v3.0.1)."""

from __future__ import annotations

from pyd3js_color import hsl, rgb

from pyd3js_interpolate import interpolateHslLong


def test_interpolate_hsl_long() -> None:
    assert interpolateHslLong("steelblue", "brown")(0) == str(rgb("steelblue"))
    assert interpolateHslLong("steelblue", hsl("brown"))(1) == str(rgb("brown"))
    assert interpolateHslLong("steelblue", rgb("brown"))(1) == str(rgb("brown"))

    assert interpolateHslLong("steelblue", "#f00")(0.2) == "rgb(56, 195, 162)"
    assert (
        interpolateHslLong("rgba(70, 130, 180, 1)", "rgba(255, 0, 0, 0.2)")(0.2)
        == "rgba(56, 195, 162, 0.84)"
    )

    i = interpolateHslLong("hsl(10,50%,50%)", "hsl(350,50%,50%)")
    assert i(0.0) == "rgb(191, 85, 64)"
    assert i(0.2) == "rgb(153, 191, 64)"
    assert i(0.4) == "rgb(64, 191, 119)"
    assert i(0.6) == "rgb(64, 119, 191)"
    assert i(0.8) == "rgb(153, 64, 191)"
    assert i(1.0) == "rgb(191, 64, 85)"

    assert interpolateHslLong("#f60", "#000")(0.5) == "rgb(128, 51, 0)"
    assert interpolateHslLong("#6f0", "#fff")(0.5) == "rgb(179, 255, 128)"
    assert interpolateHslLong("#000", "#f60")(0.5) == "rgb(128, 51, 0)"
    assert interpolateHslLong("#fff", "#6f0")(0.5) == "rgb(179, 255, 128)"
    assert interpolateHslLong("#ccc", "#000")(0.5) == "rgb(102, 102, 102)"
    assert interpolateHslLong("#f00", "#000")(0.5) == "rgb(128, 0, 0)"
    assert interpolateHslLong("#000", "#ccc")(0.5) == "rgb(102, 102, 102)"
    assert interpolateHslLong("#000", "#f00")(0.5) == "rgb(128, 0, 0)"
    assert interpolateHslLong(None, hsl(20, 1.0, 0.5))(0.5) == "rgb(255, 85, 0)"
    assert interpolateHslLong(hsl(20, 1.0, 0.5), None)(0.5) == "rgb(255, 85, 0)"
