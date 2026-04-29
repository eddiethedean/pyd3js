"""D3-compatible `rollup`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pyd3js_array._nest import NestMap
from pyd3js_array.group import group

T = TypeVar("T")
R = TypeVar("R")


def rollup(
    values: list[T],
    reduce: Callable[[list[T]], R],
    *keys: Callable[[T], Any],
) -> dict[Any, Any]:
    """Group and reduce values into a nested mapping.

    Mirrors `d3.rollup(values, reduce, ...keys)`.
    """

    g = group(values, *keys)

    def apply(node: Any) -> Any:
        if isinstance(node, NestMap):
            out: NestMap = NestMap()
            for k, v in node.items():
                out[k] = apply(v)
            return out
        return reduce(node)

    return apply(g)
