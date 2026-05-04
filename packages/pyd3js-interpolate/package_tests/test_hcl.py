from __future__ import annotations

from pyd3js_color import hcl, rgb

from pyd3js_interpolate import interpolateHcl


def test_interpolate_hcl() -> None:
    assert interpolateHcl("steelblue", "brown")(0) == str(rgb("steelblue"))
    assert interpolateHcl("steelblue", hcl("brown"))(1) == str(rgb("brown"))
    assert interpolateHcl("steelblue", rgb("brown"))(1) == str(rgb("brown"))

    assert interpolateHcl("steelblue", "#f00")(0.2) == "rgb(106, 121, 206)"
    assert (
        interpolateHcl("rgba(70, 130, 180, 1)", "rgba(255, 0, 0, 0.2)")(0.2)
        == "rgba(106, 121, 206, 0.84)"
    )

    i = interpolateHcl(hcl(10, 50, 50), hcl(350, 50, 50))
    assert i(0.0) == "rgb(194, 78, 107)"
    assert i(0.2) == "rgb(194, 78, 113)"
    assert i(0.4) == "rgb(193, 78, 118)"
    assert i(0.6) == "rgb(192, 78, 124)"
    assert i(0.8) == "rgb(191, 78, 130)"
    assert i(1.0) == "rgb(189, 79, 136)"

    i = interpolateHcl(hcl(10, 50, 50), hcl(380, 50, 50))
    assert i(0.0) == "rgb(194, 78, 107)"
    assert i(1.0) == "rgb(194, 80, 93)"

    i = interpolateHcl(hcl(10, 50, 50), hcl(710, 50, 50))
    assert i(1.0) == "rgb(189, 79, 136)"

    i = interpolateHcl(hcl(10, 50, 50), hcl(740, 50, 50))
    assert i(1.0) == "rgb(194, 80, 93)"

    assert (
        interpolateHcl("#f60", hcl(float("nan"), float("nan"), 0))(0.5)
        == "rgb(155, 0, 0)"
    )
    assert (
        interpolateHcl("#6f0", hcl(float("nan"), float("nan"), 0))(0.5)
        == "rgb(0, 129, 0)"
    )
    assert (
        interpolateHcl(hcl(float("nan"), float("nan"), 0), "#f60")(0.5)
        == "rgb(155, 0, 0)"
    )
    assert (
        interpolateHcl(hcl(float("nan"), float("nan"), 0), "#6f0")(0.5)
        == "rgb(0, 129, 0)"
    )
    assert (
        interpolateHcl("#ccc", hcl(float("nan"), float("nan"), 0))(0.5)
        == "rgb(97, 97, 97)"
    )
    assert (
        interpolateHcl("#f00", hcl(float("nan"), float("nan"), 0))(0.5)
        == "rgb(166, 0, 0)"
    )
    assert (
        interpolateHcl(hcl(float("nan"), float("nan"), 0), "#ccc")(0.5)
        == "rgb(97, 97, 97)"
    )
    assert (
        interpolateHcl(hcl(float("nan"), float("nan"), 0), "#f00")(0.5)
        == "rgb(166, 0, 0)"
    )
    assert interpolateHcl(None, hcl(20, 80, 50))(0.5) == "rgb(230, 13, 79)"
    assert interpolateHcl(hcl(20, 80, 50), None)(0.5) == "rgb(230, 13, 79)"
