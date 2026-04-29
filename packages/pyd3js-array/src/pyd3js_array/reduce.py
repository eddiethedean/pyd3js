"""D3-compatible `reduce`."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator
from typing import TypeVar, overload

T = TypeVar("T")
U = TypeVar("U")

_MISSING = object()


@overload
def reduce(values: Iterable[T], reducer: Callable[[T, T, int, Iterable[T]], T]) -> T | None: ...


@overload
def reduce(
    values: Iterable[T],
    reducer: Callable[[U, T, int, Iterable[T]], U],
    value: U,
) -> U: ...


def reduce(values: Iterable[T], reducer: Callable[..., object], value: object = _MISSING):
    """Reduce *values* using *reducer(acc, value, index, values)*.

    Mirrors `d3.reduce(values, reducer[, value])`.

    Note: D3 returns `undefined` for empty iterables without an initial value;
    in Python we return `None`.
    """

    if not callable(reducer):
        raise TypeError("reducer is not a function")

    it: Iterator[T] = iter(values)
    index = -1

    if value is _MISSING:
        try:
            value = next(it)
        except StopIteration:
            return None
        index = 0

    for next_value in it:
        index += 1
        value = reducer(value, next_value, index, values)
    return value

