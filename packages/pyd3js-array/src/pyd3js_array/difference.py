"""D3-compatible `difference`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def difference(values: Iterable[Any], other: Iterable[Any]) -> list[Any]:
    """Return the ordered set difference of *values* minus *other*.

    Order follows first appearance in *values*, with duplicates removed.
    """

    other_set = set(other)
    out: list[Any] = []
    seen: set[Any] = set()
    for v in values:
        if v in seen or v in other_set:
            continue
        seen.add(v)
        out.append(v)
    return out

