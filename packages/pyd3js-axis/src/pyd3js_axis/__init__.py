"""pyd3js-axis — Python port of d3-axis."""

from pyd3js_axis._axis import axis_bottom, axis_left, axis_right, axis_top

__version__ = "0.1.0"

axisTop = axis_top
axisRight = axis_right
axisBottom = axis_bottom
axisLeft = axis_left

__all__ = (
    "__version__",
    "axisTop",
    "axisRight",
    "axisBottom",
    "axisLeft",
)
