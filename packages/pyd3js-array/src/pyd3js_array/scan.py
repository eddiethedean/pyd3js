"""D3-compatible `scan`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

from pyd3js_array.ascending import ascending


def scan(values: Iterable[Any], compare: Callable[[Any, Any], Any] | None = None) -> int | None:
    """Return the index of the least element in *values*, or `None` if empty.

    Mirrors `d3.scan(values[, compare])`.
    """

    xs = list(values)
    if not xs:
        return None
    cmp = ascending if compare is None else compare
    best_i = 0
    best = xs[0]
    for i in range(1, len(xs)):
        v = xs[i]
        if cmp(v, best) < 0:
            best = v
            best_i = i
    return best_i

