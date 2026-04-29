from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array.quantile import quantile


def median(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    return quantile(values, 0.5, valueof)
