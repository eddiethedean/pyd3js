from __future__ import annotations

from pyd3js_color import hsl, rgb

from pyd3js_interpolate import interpolateRgb


def test_interpolate_rgb() -> None:
    assert interpolateRgb("steelblue", "brown")(0) == str(rgb("steelblue"))
    assert interpolateRgb("steelblue", hsl("brown"))(1) == str(rgb("brown"))
    assert interpolateRgb("steelblue", rgb("brown"))(1) == str(rgb("brown"))

    assert interpolateRgb("steelblue", "#f00")(0.2) == "rgb(107, 104, 144)"
    assert (
        interpolateRgb("rgba(70, 130, 180, 1)", "rgba(255, 0, 0, 0.2)")(0.2)
        == "rgba(107, 104, 144, 0.84)"
    )

    assert interpolateRgb(None, rgb(20, 40, 60))(0.5) == str(rgb(20, 40, 60))
    assert interpolateRgb(rgb(float("nan"), 20, 40), rgb(60, 80, 100))(0.5) == str(
        rgb(60, 50, 70)
    )
    assert interpolateRgb(rgb(20, float("nan"), 40), rgb(60, 80, 100))(0.5) == str(
        rgb(40, 80, 70)
    )
    assert interpolateRgb(rgb(20, 40, float("nan")), rgb(60, 80, 100))(0.5) == str(
        rgb(40, 60, 100)
    )

    assert interpolateRgb(rgb(20, 40, 60), None)(0.5) == str(rgb(20, 40, 60))
    assert interpolateRgb(rgb(60, 80, 100), rgb(float("nan"), 20, 40))(0.5) == str(
        rgb(60, 50, 70)
    )
    assert interpolateRgb(rgb(60, 80, 100), rgb(20, float("nan"), 40))(0.5) == str(
        rgb(40, 80, 70)
    )
    assert interpolateRgb(rgb(60, 80, 100), rgb(20, 40, float("nan")))(0.5) == str(
        rgb(40, 60, 100)
    )

    assert interpolateRgb.gamma(3)("steelblue", "#f00")(0.2) == "rgb(153, 121, 167)"
    assert interpolateRgb.gamma(3)("transparent", "#f00")(0.2) == "rgba(255, 0, 0, 0.2)"

    class G:
        def __float__(self) -> float:
            return 3.0

    assert interpolateRgb.gamma(G())("steelblue", "#f00")(0.2) == "rgb(153, 121, 167)"

    i0 = interpolateRgb.gamma(1)("purple", "orange")
    i1 = interpolateRgb("purple", "orange")
    for tt in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        assert i1(tt) == i0(tt)
