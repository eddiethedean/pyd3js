"""Internal typing helpers for `pyd3js-array`.

These aliases are *not* part of the public API, but they let us keep the external
D3-compatible surface flexible while still giving `ty`/type checkers something
useful to validate:

- **Comparators** return a numeric sign (negative/zero/positive), matching D3.
- **Accessors** use D3's `(value, index, values)` calling convention.
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
