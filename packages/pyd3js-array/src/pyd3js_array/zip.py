"""D3-compatible `zip`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def zip(*iterables: Iterable[Any]) -> list[list[Any]]:  # noqa: A001
    """Zip iterables together, truncating to the shortest.

    Mirrors `d3.zip(...)`.
    """

    lists = [list(it) for it in iterables]
    if not lists:
        return []
    n = min(len(x) for x in lists)
    return [[x[i] for x in lists] for i in range(n)]

