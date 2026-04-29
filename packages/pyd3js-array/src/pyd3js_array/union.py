"""D3-compatible `union`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T", bound=object)


def union(*iterables: Iterable[T]) -> list[T]:
    """Return the ordered union of all values in *iterables*.

    Mirrors `d3.union` iteration order semantics by preserving first appearance order.
    """

    seen: set[T] = set()
    out: list[T] = []
    for it in iterables:
        for v in it:
            if v in seen:
                continue
            seen.add(v)
            out.append(v)
    return out
