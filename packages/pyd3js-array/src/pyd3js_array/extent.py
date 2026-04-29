from __future__ import annotations

from typing import Any, Callable, Optional, Tuple, Union

from pyd3js_array._compare import Accessor, definite, gt, lt

Maybe = Union[Any, None]


def extent(
    values: list[Any],
    valueof: Optional[Callable[[Any, int, list[Any]], Any]] = None,
) -> Tuple[Maybe, Maybe]:
    min_v: Maybe = None
    max_v: Maybe = None
    if valueof is None:
        for value in values:
            if value is None:
                continue
            if not definite(value):
                continue
            if min_v is None:
                min_v = max_v = value
            else:
                if gt(min_v, value):
                    min_v = value
                if lt(max_v, value):
                    max_v = value
    else:
        idx = -1
        for item in values:
            idx += 1
            value = valueof(item, idx, values)
            if value is None:
                continue
            if not definite(value):
                continue
            if min_v is None:
                min_v = max_v = value
            else:
                if gt(min_v, value):
                    min_v = value
                if lt(max_v, value):
                    max_v = value
    return (min_v, max_v)
