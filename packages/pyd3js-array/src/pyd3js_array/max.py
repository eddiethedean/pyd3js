from __future__ import annotations

from typing import Any, Callable, Optional

from pyd3js_array._compare import definite, lt


def max_(
    values: list[Any],
    valueof: Optional[Callable[[Any, int, list[Any]], Any]] = None,
) -> Any:
    out: Any = None
    if valueof is None:
        for value in values:
            if value is None:
                continue
            if not definite(value):
                continue
            if out is None:
                out = value
            elif lt(out, value):
                out = value
    else:
        index = -1
        for item in values:
            index += 1
            value = valueof(item, index, values)
            if value is None:
                continue
            if not definite(value):
                continue
            if out is None:
                out = value
            elif lt(out, value):
                out = value
    return out
