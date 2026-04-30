"""Tests for `gray`, `lch`, and `cubehelix` (ports of upstream `gray-test.js`, `lch-test.js`, `cubehelix-test.js`)."""

from __future__ import annotations

import math

from pyd3js_color import cubehelix, gray, lch, rgb
from pyd3js_color.color import Color
from pyd3js_color.cubehelix import Cubehelix

from asserts import assert_hcl_equal, assert_lab_equal


def test_gray_alias() -> None:
    assert_lab_equal(gray(120), 120, 0, 0, 1)
    assert_lab_equal(gray(120, 0.5), 120, 0, 0, 0.5)
    assert_lab_equal(gray(120, None), 120, 0, 0, 1)


def test_lch_roundtrip() -> None:
    assert_hcl_equal(lch("#abc"), 252.37145234745182, 11.223567114593477, 74.96879980931759, 1)
    assert_hcl_equal(lch(rgb("#abc")), 252.37145234745182, 11.223567114593477, 74.96879980931759, 1)
    assert_hcl_equal(lch(74, 11, 252), 252, 11, 74, 1)
    assert_hcl_equal(lch(74, 11, 252, None), 252, 11, 74, 1)
    assert_hcl_equal(lch(74, 11, 252, 0.5), 252, 11, 74, 0.5)


def test_cubehelix_type_and_color_string() -> None:
    c = cubehelix("steelblue")
    assert isinstance(c, Cubehelix)
    assert isinstance(c, Color)
    assert math.isfinite(c.h)
