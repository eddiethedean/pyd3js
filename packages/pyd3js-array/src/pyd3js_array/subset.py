"""D3-compatible `subset`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def subset(a: Iterable[Any], b: Iterable[Any]) -> bool:
    """Return True if every value in *a* is in *b*."""

    bs = set(b)
    for v in a:
        if v not in bs:
            return False
    return True

