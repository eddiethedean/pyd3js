from __future__ import annotations

from pyd3js_interpolate import interpolateTransformCss, interpolateTransformSvg


def test_interpolate_transform_css_matrix_and_translate() -> None:
    s = interpolateTransformCss(
        "matrix(1.0, 2.0, 3.0, 4.0, 5.0, 6.0)",
        "translate(3px,90px)",
    )(0.5)
    assert "translate(" in s and "rotate(" in s and "skewX(" in s and "scale(" in s


def test_interpolate_transform_svg_matrix() -> None:
    s = interpolateTransformSvg("matrix(1,0,0,1,10,20)", "matrix(1,0,0,1,30,40)")(0.5)
    assert "translate(" in s
