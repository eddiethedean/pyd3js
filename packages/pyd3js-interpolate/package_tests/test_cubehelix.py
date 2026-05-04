from __future__ import annotations

from pyd3js_color import cubehelix, hcl, rgb

from pyd3js_interpolate import interpolateCubehelix


def test_interpolate_cubehelix() -> None:
    assert interpolateCubehelix("steelblue", "brown")(0) == str(rgb("steelblue"))
    assert interpolateCubehelix("steelblue", hcl("brown"))(1) == str(rgb("brown"))
    assert interpolateCubehelix("steelblue", rgb("brown"))(1) == str(rgb("brown"))

    assert interpolateCubehelix("steelblue", "#f00")(0.2) == "rgb(88, 100, 218)"
    assert (
        interpolateCubehelix("rgba(70, 130, 180, 1)", "rgba(255, 0, 0, 0.2)")(0.2)
        == "rgba(88, 100, 218, 0.84)"
    )

    assert (
        interpolateCubehelix.gamma(3)("steelblue", "#f00")(0.2) == "rgb(96, 107, 228)"
    )

    class G:
        def __float__(self) -> float:
            return 3.0

    assert (
        interpolateCubehelix.gamma(G())("steelblue", "#f00")(0.2) == "rgb(96, 107, 228)"
    )

    i0 = interpolateCubehelix.gamma(1)("purple", "orange")
    i1 = interpolateCubehelix("purple", "orange")
    for tt in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        assert i1(tt) == i0(tt)

    i = interpolateCubehelix("purple", "orange")
    assert i(0.0) == "rgb(128, 0, 128)"
    assert i(0.2) == "rgb(208, 1, 127)"
    assert i(1.0) == "rgb(255, 165, 0)"

    assert (
        interpolateCubehelix("#f60", cubehelix(float("nan"), float("nan"), 0))(0.5)
        == "rgb(162, 41, 0)"
    )
    assert interpolateCubehelix(None, cubehelix(20, 1.5, 0.5))(0.5) == "rgb(248, 93, 0)"
