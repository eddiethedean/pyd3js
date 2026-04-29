"""pyd3js-array — Python port of d3-array."""

from pyd3js_array.deviation import deviation
from pyd3js_array.extent import extent
from pyd3js_array.greatest import greatest
from pyd3js_array.greatest_index import greatestIndex
from pyd3js_array.max import max_ as max
from pyd3js_array.mean import mean
from pyd3js_array.median import median
from pyd3js_array.least import least
from pyd3js_array.least_index import leastIndex
from pyd3js_array.min import min_ as min
from pyd3js_array.quantile import quantile
from pyd3js_array.quantile_sorted import quantileSorted
from pyd3js_array.range import range_ as range
from pyd3js_array.sum import sum_ as sum
from pyd3js_array.variance import variance

__version__ = "0.0.1"

__all__ = [
    "__version__",
    "deviation",
    "extent",
    "greatest",
    "greatestIndex",
    "least",
    "leastIndex",
    "max",
    "mean",
    "median",
    "min",
    "quantile",
    "quantileSorted",
    "range",
    "sum",
    "variance",
]
