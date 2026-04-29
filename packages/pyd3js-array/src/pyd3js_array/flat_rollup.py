"""D3-compatible `flatRollup`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pyd3js_array.flat_group import _flatten
from pyd3js_array.rollups import rollups

T = TypeVar("T")
R = TypeVar("R")


def flatRollup(
    values: list[T],
    reduce: Callable[[list[T]], R],
    *keys: Callable[[T], Any],
) -> list[list[Any]]:
    """Group and reduce values, returning a flattened list of key-path rows.

    Mirrors `d3.flatRollup(values, reduce, ...keys)`.
    """

    return _flatten(rollups(values, reduce, *keys), len(keys))


__all__ = ["flatRollup"]
