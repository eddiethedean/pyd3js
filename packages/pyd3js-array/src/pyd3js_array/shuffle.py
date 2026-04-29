"""D3-compatible `shuffle`."""

from __future__ import annotations

import random
from collections.abc import MutableSequence
from typing import TypeVar

from pyd3js_array.shuffler import shuffler

T = TypeVar("T")


def shuffle(
    array: MutableSequence[T], start: int = 0, stop: int | None = None
) -> MutableSequence[T]:
    """Shuffle *array* in-place (Fisher–Yates) and return it.

    Matches `d3.shuffle(array, start, stop)` behavior.
    """
    return shuffler(random.random)(array, start, stop)
