"""
pyd3js-contour — Python port of d3-contour.

Public API matches `d3-contour` ESM (`src/index.js`): named exports only.
"""

from pyd3js_contour.contours import contours
from pyd3js_contour.density import contourDensity

__all__ = ["contours", "contourDensity", "__version__"]

__version__ = "0.1.0"
