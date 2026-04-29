"""D3-compatible `shuffle`."""

from __future__ import annotations

import random
from collections.abc import MutableSequence
from typing import Any

from pyd3js_array.shuffler import shuffler


def shuffle(array: MutableSequence[Any], start: int = 0, stop: int | None = None):
    """Shuffle *array* in-place (Fisher–Yates) and return it.

    Matches `d3.shuffle(array, start, stop)` behavior.
    """
    return shuffler(random.random)(array, start, stop)

