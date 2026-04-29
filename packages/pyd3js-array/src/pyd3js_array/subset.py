"""D3-compatible `subset`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T", bound=object)


def subset(a: Iterable[T], b: Iterable[T]) -> bool:
    """Return True if every value in *a* is in *b*."""

    bs = set(b)
    for v in a:
        if v not in bs:
            return False
    return True
