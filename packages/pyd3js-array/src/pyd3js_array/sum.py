from __future__ import annotations

from collections.abc import Callable
from typing import Any

from pyd3js_array._iter import iter_observed_numbers


def sum_(
    values: list[Any],
    valueof: Callable[[Any, int, list[Any]], Any] | None = None,
) -> float:
    out = 0.0
    for n in iter_observed_numbers(values, valueof):
        out += n
    return out
