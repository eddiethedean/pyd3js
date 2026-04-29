"""D3-compatible `merge`."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


def _flatten(arrays: Iterable[Iterable[T]]) -> Iterator[T]:
    for array in arrays:
        yield from array


def merge(arrays: Iterable[Iterable[T]]) -> list[T]:
    """Flatten *arrays* by one level.

    Mirrors `d3.merge(arrays)`.
    """

    return list(_flatten(arrays))

