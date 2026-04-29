"""D3-compatible `flatGroup`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pyd3js_array.groups import groups

T = TypeVar("T")


def _flatten(group_rows: list[list[Any]], nkeys: int) -> list[list[Any]]:
    out = group_rows
    for _depth in range(1, nkeys):
        next_out: list[list[Any]] = []
        for row in out:
            tail = row[-1]
            prefix = row[:-1]
            # tail is a list of [key, value] pairs
            for k, v in tail:
                next_out.append([*prefix, k, v])
        out = next_out
    return out


def flatGroup(values: list[T], *keys: Callable[[T], Any]) -> list[list[Any]]:
    """Group *values* and return a flattened list of key-path rows.

    Mirrors `d3.flatGroup(values, ...keys)`.
    """

    return _flatten(groups(values, *keys), len(keys))


__all__ = ["flatGroup"]
