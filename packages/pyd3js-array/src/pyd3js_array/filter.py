"""D3-compatible `filter`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def filter(values: Iterable[T], test: Callable[[T, int, Iterable[T]], bool]) -> list[T]:
    """Filter *values* using *test(value, index, values)*.

    Mirrors `d3.filter(values, test)`.
    """

    if not callable(test):
        raise TypeError("test is not a function")

    out: list[T] = []
    for index, value in enumerate(values):
        if test(value, index, values):
            out.append(value)
    return out
