"""Internal typing helpers for `pyd3js-array`.

These are intentionally small and pragmatic: the public API mirrors D3, which is
quite dynamic, but we still want type checking to catch obvious mistakes.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Protocol, TypeAlias, TypeVar

T = TypeVar("T")
R = TypeVar("R")

CompareResult: TypeAlias = float | int
CompareFn: TypeAlias = Callable[[T, T], CompareResult]

# D3-style accessor functions often receive (value, index, values).
AccessorFn: TypeAlias = Callable[[T, int, Sequence[T]], R]


class SupportsOrdering(Protocol):
    def __lt__(self, other: object, /) -> bool: ...

    def __gt__(self, other: object, /) -> bool: ...
