from __future__ import annotations

import math

import pytest

from pyd3js_array.blur import blur, blur2, blurImage


def test_blur_noop_for_zero_radius() -> None:
    a = [1.0, 2.0, 3.0]
    assert blur(a, 0) is a
    assert a == [1.0, 2.0, 3.0]


def test_blur_mutates_in_place() -> None:
    a = [0.0, 0.0, 10.0, 0.0, 0.0]
    out = blur(a, 1)
    assert out is a
    assert a[2] < 10.0


def test_blur2_mutates_data_in_place() -> None:
    img = {"data": [0.0, 0.0, 10.0, 0.0], "width": 2, "height": 2}
    out = blur2(img, 1)
    assert out is img
    assert out["data"][2] < 10.0


@pytest.mark.oracle
def test_blur_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    a = [0.0, 0.0, 10.0, 0.0, 0.0]
    py = a[:]
    blur(py, 1)
    js = oracle_eval(
        "(function(){ const a=[0,0,10,0,0]; d3.blur(a,1); return a; })()"
    )
    assert len(py) == len(js)
    for x, y in zip(py, js):
        assert math.isclose(x, y, rel_tol=1e-12, abs_tol=1e-12)


@pytest.mark.oracle
def test_blur2_blurimage_match_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    py = {"data": [0.0, 0.0, 10.0, 0.0], "width": 2, "height": 2}
    blur2(py, 1)
    js = oracle_eval(
        "(function(){ const o={data:[0,0,10,0],width:2,height:2}; d3.blur2(o,1); return o; })()"
    )
    for x, y in zip(py["data"], js["data"]):
        assert math.isclose(x, y, rel_tol=1e-12, abs_tol=1e-12)

    # RGBA "image": 2 pixels wide, 1 high
    py_img = {"data": [255.0, 0.0, 0.0, 255.0, 0.0, 0.0, 255.0, 255.0], "width": 2, "height": 1}
    blurImage(py_img, 1)
    js_img = oracle_eval(
        "(function(){ const o={data:[255,0,0,255,0,0,255,255],width:2,height:1}; d3.blurImage(o,1); return o; })()"
    )
    for x, y in zip(py_img["data"], js_img["data"]):
        assert math.isclose(x, y, rel_tol=1e-12, abs_tol=1e-12)

