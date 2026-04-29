from __future__ import annotations

from typing import Any

from pyd3js_array._iter import iter_observed
from pyd3js_array._ordering import CompareFn, default_compare


def greatest(values: list[Any], compare: CompareFn | None = None) -> Any | None:
    if compare is None:
        compare = default_compare

    it = iter_observed(values)
    best = next(it, None)
    if best is None:
        return None
    for v in it:
        if compare(v, best) > 0:
            best = v
    return best
