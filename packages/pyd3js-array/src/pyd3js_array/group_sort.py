"""D3-compatible `groupSort`."""

from __future__ import annotations

from collections.abc import Callable
from functools import cmp_to_key
from typing import Any, TypeVar

from pyd3js_array.ascending import ascending
from pyd3js_array.group import group

T = TypeVar("T")
K = TypeVar("K")
R = TypeVar("R")


def groupSort(
    values: list[T],
    reduce: Callable[[list[T]], R],
    key: Callable[[T], K],
    compare: Callable[[Any, Any], Any] | None = None,
) -> list[K]:
    """Return keys ordered by the reduced value for each group.

    Mirrors `d3.groupSort(values, reduce, key[, compare])`.
    """

    g = group(values, key)
    items: list[tuple[K, R]] = [(k, reduce(v)) for k, v in g.items()]
    cmp = ascending if compare is None else compare

    def cmp_int(a: tuple[K, R], b: tuple[K, R]) -> int:
        r = cmp(a[1], b[1])
        if r < 0:
            return -1
        if r > 0:
            return 1
        return 0

    items.sort(key=cmp_to_key(cmp_int))
    return [k for k, _ in items]
