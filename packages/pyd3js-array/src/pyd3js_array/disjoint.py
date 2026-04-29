"""D3-compatible `disjoint`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T", bound=object)


def disjoint(a: Iterable[T], b: Iterable[T]) -> bool:
    """Return True if *a* and *b* share no values."""

    aset = set(a)
    for v in b:
        if v in aset:
            return False
    return True
