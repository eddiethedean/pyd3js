"""pyd3js-interpolate — Python port of d3-interpolate."""

from __future__ import annotations

from pyd3js_interpolate.array import generic_array, interpolate_array
from pyd3js_interpolate.basis import basis_fn, interpolate_basis
from pyd3js_interpolate.basis_closed import interpolate_basis_closed
from pyd3js_interpolate.cubehelix import (
    interpolate_cubehelix,
    interpolate_cubehelix_long,
)
from pyd3js_interpolate.date import interpolate_date
from pyd3js_interpolate.discrete import interpolate_discrete
from pyd3js_interpolate.hcl import interpolate_hcl, interpolate_hcl_long
from pyd3js_interpolate.hsl import interpolate_hsl, interpolate_hsl_long
from pyd3js_interpolate.hue import interpolate_hue
from pyd3js_interpolate.lab import interpolate_lab
from pyd3js_interpolate.number import interpolate_number
from pyd3js_interpolate.number_array import interpolate_number_array, is_number_array
from pyd3js_interpolate.object import interpolate_object
from pyd3js_interpolate.piecewise import piecewise
from pyd3js_interpolate.quantize import quantize
from pyd3js_interpolate.rgb import (
    interpolate_rgb,
    interpolate_rgb_basis,
    interpolate_rgb_basis_closed,
)
from pyd3js_interpolate.round import interpolate_round
from pyd3js_interpolate.string import interpolate_string
from pyd3js_interpolate.transform import (
    interpolate_transform_css,
    interpolate_transform_svg,
)
from pyd3js_interpolate.value import interpolate_value
from pyd3js_interpolate.zoom import interpolate_zoom

__version__ = "0.1.0"

# d3-interpolate-style camelCase aliases (API parity)
interpolate = interpolate_value
interpolateArray = interpolate_array
interpolateBasis = interpolate_basis
interpolateBasisClosed = interpolate_basis_closed
interpolateCubehelix = interpolate_cubehelix
interpolateCubehelixLong = interpolate_cubehelix_long
interpolateDate = interpolate_date
interpolateDiscrete = interpolate_discrete
interpolateHcl = interpolate_hcl
interpolateHclLong = interpolate_hcl_long
interpolateHsl = interpolate_hsl
interpolateHslLong = interpolate_hsl_long
interpolateHue = interpolate_hue
interpolateLab = interpolate_lab
interpolateNumber = interpolate_number
interpolateNumberArray = interpolate_number_array
interpolateObject = interpolate_object
interpolateRgb = interpolate_rgb
interpolateRgbBasis = interpolate_rgb_basis
interpolateRgbBasisClosed = interpolate_rgb_basis_closed
interpolateRound = interpolate_round
interpolateString = interpolate_string
interpolateTransformCss = interpolate_transform_css
interpolateTransformSvg = interpolate_transform_svg
interpolateZoom = interpolate_zoom

__all__ = (
    "__version__",
    "basis_fn",
    "generic_array",
    "interpolate",
    "interpolateArray",
    "interpolateBasis",
    "interpolateBasisClosed",
    "interpolateCubehelix",
    "interpolateCubehelixLong",
    "interpolateDate",
    "interpolateDiscrete",
    "interpolateHcl",
    "interpolateHclLong",
    "interpolateHsl",
    "interpolateHslLong",
    "interpolateHue",
    "interpolateLab",
    "interpolateNumber",
    "interpolateNumberArray",
    "interpolateObject",
    "interpolateRgb",
    "interpolateRgbBasis",
    "interpolateRgbBasisClosed",
    "interpolateRound",
    "interpolateString",
    "interpolateTransformCss",
    "interpolateTransformSvg",
    "interpolateZoom",
    "interpolate_array",
    "interpolate_basis",
    "interpolate_basis_closed",
    "interpolate_cubehelix",
    "interpolate_cubehelix_long",
    "interpolate_date",
    "interpolate_discrete",
    "interpolate_hcl",
    "interpolate_hcl_long",
    "interpolate_hsl",
    "interpolate_hsl_long",
    "interpolate_hue",
    "interpolate_lab",
    "interpolate_number",
    "interpolate_number_array",
    "interpolate_object",
    "interpolate_rgb",
    "interpolate_rgb_basis",
    "interpolate_rgb_basis_closed",
    "interpolate_round",
    "interpolate_string",
    "interpolate_transform_css",
    "interpolate_transform_svg",
    "interpolate_value",
    "interpolate_zoom",
    "is_number_array",
    "isNumberArray",
    "piecewise",
    "quantize",
)

isNumberArray = is_number_array
