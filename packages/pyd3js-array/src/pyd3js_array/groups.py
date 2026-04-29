"""D3-compatible `groups`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pyd3js_array._nest import NestMap
from pyd3js_array.group import group

T = TypeVar("T")


def groups(values: list[T], *keys: Callable[[T], Any]) -> list[list[Any]]:
    """Group *values* into a nested list of `[key, value]` pairs.

    Mirrors `d3.groups(values, ...keys)`:
    - For one key, returns `[[k, [values...]], ...]` in insertion order.
    - For multiple keys, returns nested `[[k, groups(...)], ...]`.
    """

    g = group(values, *keys)

    def to_pairs(node: Any) -> Any:
        if isinstance(node, NestMap):
            return [[k, to_pairs(v)] for k, v in node.items()]
        return node

    return to_pairs(g)
