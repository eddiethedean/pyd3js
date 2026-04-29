from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._iter import iter_observed_numbers


def mean(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float | None:
    total = 0.0
    count = 0
    for n in iter_observed_numbers(values, valueof):
        total += n
        count += 1
    if count == 0:
        return None
    return total / count
