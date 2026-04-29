"""D3-compatible `intersection`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def intersection(*iterables: Iterable[Any]) -> list[Any]:
    """Return the ordered intersection of all iterables.

    Order follows first appearance in the first iterable, with duplicates removed.
    """

    if not iterables:
        return []

    it0, *rest = iterables
    rest_sets = [set(it) for it in rest]
    out: list[Any] = []
    seen: set[Any] = set()
    for v in it0:
        if v in seen:
            continue
        if all(v in s for s in rest_sets):
            out.append(v)
            seen.add(v)
    return out

