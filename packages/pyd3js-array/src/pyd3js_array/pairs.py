"""D3-compatible `pairs`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def pairs(values: Iterable[T], reduce: Callable[[T, T], R] | None = None) -> list[Any]:
    """Return adjacent pairs from *values*.

    Mirrors `d3.pairs(values[, reduce])`.
    """

    xs = list(values)
    if len(xs) < 2:
        return []
    if reduce is None:
        return [[xs[i - 1], xs[i]] for i in range(1, len(xs))]
    return [reduce(xs[i - 1], xs[i]) for i in range(1, len(xs))]
