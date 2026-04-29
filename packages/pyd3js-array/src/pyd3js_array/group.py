"""D3-compatible `group`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar, cast

from pyd3js_array._nest import NestMap

T = TypeVar("T")


def group(values: list[T], *keys: Callable[[T], Any]) -> NestMap:
    """Group *values* into a nested mapping keyed by one or more key functions.

    Mirrors `d3.group(values, ...keys)`:
    - For one key, returns `{key: [values...]}`.
    - For multiple keys, returns nested dicts; leaf values are lists.
    """

    if len(keys) == 0:
        raise TypeError("group() requires at least one key function")

    def regroup(vs: list[T], depth: int) -> Any:
        if depth >= len(keys):
            return list(vs)
        out: NestMap = NestMap()
        key_fn = keys[depth]
        for v in vs:
            k = key_fn(v)
            bucket = out.get(k)
            if bucket is None:
                out[k] = [v]
            else:
                bucket.append(v)
        for k, bucket in list(out.items()):
            out[k] = regroup(bucket, depth + 1)
        return out

    return cast(NestMap, regroup(values, 0))

