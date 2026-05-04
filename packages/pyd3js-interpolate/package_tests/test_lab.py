from __future__ import annotations

from pyd3js_color import hsl, lab, rgb

from pyd3js_interpolate import interpolateLab


def test_interpolate_lab() -> None:
    assert interpolateLab("steelblue", "brown")(0) == str(rgb("steelblue"))
    assert interpolateLab("steelblue", hsl("brown"))(1) == str(rgb("brown"))
    assert interpolateLab("steelblue", rgb("brown"))(1) == str(rgb("brown"))

    assert interpolateLab("steelblue", "#f00")(0.2) == "rgb(134, 120, 146)"
    assert (
        interpolateLab("rgba(70, 130, 180, 1)", "rgba(255, 0, 0, 0.2)")(0.2)
        == "rgba(134, 120, 146, 0.84)"
    )

    assert interpolateLab(None, lab(20, 40, 60))(0.5) == str(lab(20, 40, 60))
    assert interpolateLab(lab(float("nan"), 20, 40), lab(60, 80, 100))(0.5) == str(
        lab(60, 50, 70)
    )
    assert interpolateLab(lab(20, float("nan"), 40), lab(60, 80, 100))(0.5) == str(
        lab(40, 80, 70)
    )
    assert interpolateLab(lab(20, 40, float("nan")), lab(60, 80, 100))(0.5) == str(
        lab(40, 60, 100)
    )

    assert interpolateLab(lab(20, 40, 60), None)(0.5) == str(lab(20, 40, 60))
    assert interpolateLab(lab(60, 80, 100), lab(float("nan"), 20, 40))(0.5) == str(
        lab(60, 50, 70)
    )
    assert interpolateLab(lab(60, 80, 100), lab(20, float("nan"), 40))(0.5) == str(
        lab(40, 80, 70)
    )
    assert interpolateLab(lab(60, 80, 100), lab(20, 40, float("nan")))(0.5) == str(
        lab(40, 60, 100)
    )
