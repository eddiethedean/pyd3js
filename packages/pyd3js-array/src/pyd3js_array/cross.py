"""D3-compatible `cross`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any, TypeVar

T = TypeVar("T")
U = TypeVar("U")
R = TypeVar("R")


def cross(
    a: Iterable[T],
    b: Iterable[U],
    reduce: Callable[[T, U], R] | None = None,
) -> list[Any]:
    """Return the cartesian product of *a* and *b*.

    Mirrors `d3.cross(a, b[, reduce])`.
    """

    aa = list(a)
    bb = list(b)
    if reduce is None:
        return [[x, y] for x in aa for y in bb]
    return [reduce(x, y) for x in aa for y in bb]

