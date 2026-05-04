from __future__ import annotations

from pyd3js_color import cubehelix, hcl, rgb

from pyd3js_interpolate import interpolateCubehelixLong


def test_interpolate_cubehelix_long() -> None:
    assert interpolateCubehelixLong("steelblue", "brown")(0) == str(rgb("steelblue"))
    assert interpolateCubehelixLong("steelblue", hcl("brown"))(1) == str(rgb("brown"))
    assert interpolateCubehelixLong("steelblue", rgb("brown"))(1) == str(rgb("brown"))

    assert interpolateCubehelixLong("steelblue", "#f00")(0.2) == "rgb(88, 100, 218)"
    assert (
        interpolateCubehelixLong.gamma(3)("steelblue", "#f00")(0.2)
        == "rgb(96, 107, 228)"
    )

    i0 = interpolateCubehelixLong.gamma(1)("purple", "orange")
    i1 = interpolateCubehelixLong("purple", "orange")
    for tt in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0):
        assert i1(tt) == i0(tt)

    i = interpolateCubehelixLong("purple", "orange")
    assert i(0.0) == "rgb(128, 0, 128)"
    assert i(0.2) == "rgb(63, 54, 234)"
    assert i(1.0) == "rgb(255, 165, 0)"

    assert (
        interpolateCubehelixLong(None, cubehelix(20, 1.5, 0.5))(0.5)
        == "rgb(248, 93, 0)"
    )
