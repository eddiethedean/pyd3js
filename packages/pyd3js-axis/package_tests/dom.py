"""Small DOM helpers for axis package tests (typed `svg` roots)."""

from __future__ import annotations

from pyd3js_axis._selection import create
from pyd3js_axis._svg import Element


def svg_root() -> Element:
    n = create("svg").node()
    assert isinstance(n, Element)
    return n
