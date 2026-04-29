"""D3-compatible `shuffler`."""

from __future__ import annotations

from collections.abc import Callable, MutableSequence
from typing import TypeVar

T = TypeVar("T")


def shuffler(random: Callable[[], float]):
    """Create a shuffle function using the provided RNG.

    Mirrors `d3.shuffler(random)`.
    """

    def shuffle(
        array: MutableSequence[T], start: int = 0, stop: int | None = None
    ) -> MutableSequence[T]:
        if stop is None:
            stop = len(array)
        i0 = int(start)
        i1 = int(stop)
        m = i1 - i0
        while m:
            m -= 1
            i = int(random() * (m + 1))
            j = m + i0
            k = i + i0
            array[j], array[k] = array[k], array[j]
        return array

    return shuffle
