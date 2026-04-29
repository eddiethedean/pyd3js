"""D3-compatible `index`."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from pyd3js_array._nest import NestMap

T = TypeVar("T")


def index(values: list[T], *keys: Callable[[T], Any]) -> NestMap:
    """Index *values* by one or more key functions.

    Mirrors `d3.index(values, ...keys)`:
    - Like `group`, but each leaf is a single value.
    - Throws on duplicate keys at the leaf level.
    """

    if len(keys) == 0:
        raise TypeError("index() requires at least one key function")

    def regroup(vs: list[T], depth: int) -> NestMap:
        key_fn = keys[depth]
        out: NestMap = NestMap()
        if depth == len(keys) - 1:
            for v in vs:
                k = key_fn(v)
                if k in out:
                    raise ValueError("duplicate key")
                out[k] = v
            return out

        buckets: NestMap = NestMap()
        for v in vs:
            k = key_fn(v)
            bucket = buckets.get(k)
            if bucket is None:
                buckets[k] = [v]
            else:
                bucket.append(v)

        for k, bucket in buckets.items():
            out[k] = regroup(bucket, depth + 1)
        return out

    return regroup(values, 0)
