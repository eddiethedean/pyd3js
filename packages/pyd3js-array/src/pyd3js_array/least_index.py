from __future__ import annotations

from typing import Any

from pyd3js_array._compare import definite
from pyd3js_array._ordering import CompareFn, default_compare


def leastIndex(values: list[Any], compare: CompareFn | None = None) -> int:
    if compare is None:
        compare = default_compare

    best: Any | None = None
    best_i: int | None = None
    for i, v in enumerate(values):
        if v is None:
            continue
        if not definite(v):
            continue
        if best is None:
            best = v
            best_i = i
        elif compare(v, best) < 0:
            best = v
            best_i = i
    return -1 if best_i is None else best_i
