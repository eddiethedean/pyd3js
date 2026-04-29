"""D3-compatible `intersection`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar


T = TypeVar("T", bound=object)


def intersection(*iterables: Iterable[T]) -> list[T]:
    """Return the ordered intersection of all iterables.

    Order follows first appearance in the first iterable, with duplicates removed.
    """

    if not iterables:
        return []

    it0, *rest = iterables
    rest_sets = [set(it) for it in rest]
    out: list[T] = []
    seen: set[T] = set()
    for v in it0:
        if v in seen:
            continue
        if all(v in s for s in rest_sets):
            out.append(v)
            seen.add(v)
    return out
