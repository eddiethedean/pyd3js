"""D3-compatible `rollups`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pyd3js_array._nest import NestMap
from pyd3js_array.rollup import rollup

T = TypeVar("T")
R = TypeVar("R")


def rollups(
    values: list[T],
    reduce: Callable[[list[T]], R],
    *keys: Callable[[T], Any],
) -> list[list[Any]]:
    """Group and reduce values into a nested list of `[key, value]` pairs.

    Mirrors `d3.rollups(values, reduce, ...keys)`.
    """

    m = rollup(values, reduce, *keys)

    def to_pairs(node: Any) -> Any:
        if isinstance(node, NestMap):
            return [[k, to_pairs(v)] for k, v in node.items()]
        return node

    return to_pairs(m)
