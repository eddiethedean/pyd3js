"""D3 in Python — umbrella package (lazy submodule access)."""

from __future__ import annotations

import importlib
from typing import Any

__version__ = "0.0.0"

_ALIASES: dict[str, str] = {
    "array": "pyd3js_array",
    "axis": "pyd3js_axis",
    "brush": "pyd3js_brush",
    "chord": "pyd3js_chord",
    "color": "pyd3js_color",
    "contour": "pyd3js_contour",
    "delaunay": "pyd3js_delaunay",
    "dispatch": "pyd3js_dispatch",
    "drag": "pyd3js_drag",
    "dsv": "pyd3js_dsv",
    "ease": "pyd3js_ease",
    "fetch": "pyd3js_fetch",
    "force": "pyd3js_force",
    "format": "pyd3js_format",
    "geo": "pyd3js_geo",
    "hierarchy": "pyd3js_hierarchy",
    "interpolate": "pyd3js_interpolate",
    "path": "pyd3js_path",
    "polygon": "pyd3js_polygon",
    "quadtree": "pyd3js_quadtree",
    "random": "pyd3js_random",
    "scale": "pyd3js_scale",
    "scaleChromatic": "pyd3js_scale_chromatic",
    "selection": "pyd3js_selection",
    "shape": "pyd3js_shape",
    "time": "pyd3js_time",
    "timeFormat": "pyd3js_time_format",
    "timer": "pyd3js_timer",
    "transition": "pyd3js_transition",
    "zoom": "pyd3js_zoom",
}


def __getattr__(name: str) -> Any:
    mod = _ALIASES.get(name)
    if mod is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    return importlib.import_module(mod)


def __dir__() -> list[str]:
    return sorted([*_ALIASES, "__version__"])
