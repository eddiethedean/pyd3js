"""D3-compatible `some`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def some(values: Iterable[T], test: Callable[[T, int, Iterable[T]], bool]) -> bool:
    """Return True if *test* passes for any element.

    Mirrors `d3.some(values, test)`.
    """

    if not callable(test):
        raise TypeError("test is not a function")
    for index, value in enumerate(values):
        if test(value, index, values):
            return True
    return False

