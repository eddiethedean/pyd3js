"""D3-compatible `superset`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def superset(a: Iterable[Any], b: Iterable[Any]) -> bool:
    """Return True if every value in *b* is in *a*."""

    aset = set(a)
    for v in b:
        if v not in aset:
            return False
    return True

