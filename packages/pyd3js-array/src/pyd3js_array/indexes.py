"""D3-compatible `indexes`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pyd3js_array._nest import NestMap
from pyd3js_array.index import index

T = TypeVar("T")


def indexes(values: list[T], *keys: Callable[[T], Any]) -> list[list[Any]]:
    """Index *values* into a nested list of `[key, value]` pairs.

    Mirrors `d3.indexes(values, ...keys)`.
    """

    m = index(values, *keys)

    def to_pairs(node: Any) -> Any:
        if isinstance(node, NestMap):
            return [[k, to_pairs(v)] for k, v in node.items()]
        return node

    return to_pairs(m)
