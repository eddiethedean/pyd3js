from __future__ import annotations

from pyd3js_color import hcl, rgb

from pyd3js_interpolate import interpolateHclLong


def test_interpolate_hcl_long() -> None:
    assert interpolateHclLong("steelblue", "brown")(0) == str(rgb("steelblue"))
    assert interpolateHclLong("steelblue", hcl("brown"))(1) == str(rgb("brown"))
    assert interpolateHclLong("steelblue", rgb("brown"))(1) == str(rgb("brown"))

    assert interpolateHclLong("steelblue", "#f00")(0.2) == "rgb(0, 144, 169)"
    assert (
        interpolateHclLong("rgba(70, 130, 180, 1)", "rgba(255, 0, 0, 0.2)")(0.2)
        == "rgba(0, 144, 169, 0.84)"
    )

    i = interpolateHclLong(hcl(10, 50, 50), hcl(350, 50, 50))
    assert i(0.0) == "rgb(194, 78, 107)"
    assert i(0.2) == "rgb(151, 111, 28)"
    assert i(0.4) == "rgb(35, 136, 68)"
    assert i(0.6) == "rgb(0, 138, 165)"
    assert i(0.8) == "rgb(91, 116, 203)"
    assert i(1.0) == "rgb(189, 79, 136)"

    assert (
        interpolateHclLong("#f60", hcl(float("nan"), float("nan"), 0))(0.5)
        == "rgb(155, 0, 0)"
    )
    assert interpolateHclLong(None, hcl(20, 80, 50))(0.5) == "rgb(230, 13, 79)"
