"""D3-compatible `every`."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TypeVar

T = TypeVar("T")


def every(values: Iterable[T], test: Callable[[T, int, Iterable[T]], bool]) -> bool:
    """Return True if *test* passes for every element.

    Mirrors `d3.every(values, test)`.
    """

    if not callable(test):
        raise TypeError("test is not a function")
    for index, value in enumerate(values):
        if not test(value, index, values):
            return False
    return True
