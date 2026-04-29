from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any

from pyd3js_array.variance import variance


def deviation(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    v = variance(values, valueof)
    if v is None:
        return None
    return math.sqrt(v)
