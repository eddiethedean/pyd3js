"""D3-compatible `rank`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from functools import cmp_to_key
from typing import Any

from pyd3js_array.ascending import ascending


def rank(
    values: Iterable[Any], compare: Callable[[Any, Any], Any] | None = None
) -> list[int]:
    """Return ranks for each value, aligned with original index.

    Mirrors `d3.rank(values[, compare])`.\n
    Equal values share the same rank.
    """

    xs = list(values)
    n = len(xs)
    idxs = list(range(n))

    cmp = ascending if compare is None else compare

    def cmp_int(i: int, j: int) -> int:
        r = cmp(xs[i], xs[j])
        if r < 0:
            return -1
        if r > 0:
            return 1
        return 0

    idxs.sort(key=cmp_to_key(cmp_int))

    out = [0] * n
    if n == 0:
        return out

    r = 0
    out[idxs[0]] = 0
    for pos in range(1, n):
        i_prev = idxs[pos - 1]
        i = idxs[pos]
        if cmp_int(i_prev, i) != 0:
            r = pos
        out[i] = r
    return out
