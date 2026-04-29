"""D3-compatible `union`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def union(*iterables: Iterable[Any]) -> list[Any]:
    """Return the ordered union of all values in *iterables*.

    Mirrors `d3.union` iteration order semantics by preserving first appearance order.
    """

    seen: set[Any] = set()
    out: list[Any] = []
    for it in iterables:
        for v in it:
            if v in seen:
                continue
            seen.add(v)
            out.append(v)
    return out

