"""D3-compatible `InternMap` and `InternSet` (Python approximation).

These types are exported mainly for parity with `d3-array`. In upstream, these
extend JS Map/Set and use "interning" to allow non-primitive keys (e.g. Dates)
to be compared by value rather than identity.

In Python, `dict`/`set` already compare many objects by value, but we still
support an explicit `key=` canonicalizer to emulate upstream `internmap` usage.
"""

from __future__ import annotations

from collections.abc import Callable, Hashable, Iterable, Iterator, MutableMapping
from typing import Any, Generic, TypeVar, overload

K = TypeVar("K")
V = TypeVar("V")
T = TypeVar("T")


def _identity(x: Any) -> Any:
    return x


class InternMap(MutableMapping[K, V], Generic[K, V]):
    """A mapping that optionally interns keys using a canonicalizer function."""

    def __init__(
        self,
        iterable: Iterable[tuple[K, V]] | None = None,
        key: Callable[[K], Hashable] | None = None,
    ) -> None:
        self._key = key or _identity
        # canonical_key -> (original_key, value)
        self._data: dict[Hashable, tuple[K, V]] = {}
        if iterable is not None:
            for k, v in iterable:
                self[k] = v

    def _canon(self, k: K) -> Hashable:
        return self._key(k)

    def __getitem__(self, k: K) -> V:
        return self._data[self._canon(k)][1]

    def __setitem__(self, k: K, v: V) -> None:
        ck = self._canon(k)
        self._data[ck] = (k, v)

    def __delitem__(self, k: K) -> None:
        del self._data[self._canon(k)]

    def __iter__(self) -> Iterator[K]:
        for k, _v in self._data.values():
            yield k

    def __len__(self) -> int:
        return len(self._data)

    # Convenience methods to mirror JS Map

    @overload
    def get(self, k: K) -> V | None: ...

    @overload
    def get(self, k: K, default: T) -> V | T: ...

    def get(self, k: K, default: T | None = None) -> V | T | None:
        try:
            return self[k]
        except KeyError:
            return default

    def set(self, k: K, v: V) -> "InternMap[K, V]":
        self[k] = v
        return self

    def has(self, k: K) -> bool:
        return self._canon(k) in self._data

    def delete(self, k: K) -> bool:
        ck = self._canon(k)
        if ck in self._data:
            del self._data[ck]
            return True
        return False


class InternSet(Generic[K]):
    """A set that optionally interns values using a canonicalizer function."""

    def __init__(
        self,
        iterable: Iterable[K] | None = None,
        key: Callable[[K], Hashable] | None = None,
    ) -> None:
        self._key = key or _identity
        # canonical_key -> original_value
        self._data: dict[Hashable, K] = {}
        if iterable is not None:
            for v in iterable:
                self.add(v)

    def _canon(self, v: K) -> Hashable:
        return self._key(v)

    def add(self, v: K) -> "InternSet[K]":
        self._data[self._canon(v)] = v
        return self

    def has(self, v: K) -> bool:
        return self._canon(v) in self._data

    def delete(self, v: K) -> bool:
        ck = self._canon(v)
        if ck in self._data:
            del self._data[ck]
            return True
        return False

    def __contains__(self, v: object) -> bool:
        try:
            return self._canon(v) in self._data  # type: ignore[arg-type]
        except Exception:
            return False

    def __iter__(self) -> Iterator[K]:
        yield from self._data.values()

    def __len__(self) -> int:
        return len(self._data)


__all__ = ["InternMap", "InternSet"]
