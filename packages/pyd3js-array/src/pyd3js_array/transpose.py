"""D3-compatible `transpose`."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from pyd3js_array.zip import zip


def transpose(matrix: Iterable[Iterable[Any]]) -> list[list[Any]]:
    """Transpose a matrix (rows to columns), truncating to the shortest row."""

    rows = [list(r) for r in matrix]
    return zip(*rows)

