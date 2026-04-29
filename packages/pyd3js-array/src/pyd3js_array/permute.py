"""D3-compatible `permute`."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TypeVar

T = TypeVar("T")


def permute(values: Sequence[T], indices: Sequence[int]) -> list[T]:
    """Return a new array containing `values[i]` for each index in *indices*."""

    return [values[i] for i in indices]

