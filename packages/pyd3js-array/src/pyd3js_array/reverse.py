"""D3-compatible `reverse`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


def reverse(values: Iterable[T]) -> list[T]:
    """Return a new reversed list of *values*.

    Mirrors `d3.reverse(values)`.
    """

    try:
        return list(values)[::-1]
    except TypeError as e:  # pragma: no cover
        raise TypeError("values is not iterable") from e
