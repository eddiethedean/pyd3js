"""D3-compatible `map`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")
U = TypeVar("U")


def map(values: Iterable[T], mapper: Callable[[T, int, Iterable[T]], U]) -> list[U]:
    """Map *values* using *mapper(value, index, values)*.

    Mirrors `d3.map(values, mapper)`.
    """

    if not callable(mapper):
        raise TypeError("mapper is not a function")
    try:
        it = iter(values)
    except TypeError as e:  # pragma: no cover
        raise TypeError("values is not iterable") from e

    out: list[U] = []
    for index, value in enumerate(it):
        out.append(mapper(value, index, values))
    return out

