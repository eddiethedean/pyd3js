"""pyd3js-array — Python port of d3-array."""

from pyd3js_array.extent import extent
from pyd3js_array.max import max_ as max
from pyd3js_array.min import min_ as min
from pyd3js_array.range import range_ as range

__version__ = "0.0.1"

__all__ = ["__version__", "extent", "max", "min", "range"]
