"""D3-compatible `shuffle`."""

from __future__ import annotations

import random
from collections.abc import MutableSequence
from typing import Any


def shuffle(array: MutableSequence[Any], start: int = 0, stop: int | None = None):
    """Shuffle *array* in-place (Fisher–Yates) and return it.

    Matches `d3.shuffle(array, start, stop)` behavior.
    """

    if stop is None:
        stop = len(array)
    i = stop - 1
    while i > start:
        j = start + int(random.random() * (i - start + 1))
        array[i], array[j] = array[j], array[i]
        i -= 1
    return array

