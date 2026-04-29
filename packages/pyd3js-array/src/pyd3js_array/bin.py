"""D3-compatible `bin()` (histogram) factory."""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass
from typing import Any, Generic, TypeVar, cast, overload

from pyd3js_array._compare import tonumber
from pyd3js_array.tick_step import tickStep

T = TypeVar("T")


class Bin(list[T]):
    """A single histogram bin with `x0`/`x1` bounds (matches D3)."""

    x0: float
    x1: float

    def __init__(self, x0: float, x1: float) -> None:
        super().__init__()
        self.x0 = x0
        self.x1 = x1


def _sturges(n: int) -> int:
    if n <= 0:
        return 1
    return int(math.ceil(math.log2(n))) + 1


def _coerce_numbers(values: Iterable[T], value: Callable[[T], Any]) -> tuple[list[T], list[float]]:
    items: list[T] = []
    nums: list[float] = []
    for v in values:
        x = value(v)
        if x is None:
            continue
        n = tonumber(x)
        if n != n:  # NaN
            continue
        items.append(v)
        nums.append(n)
    return items, nums


def _extent(nums: list[float]) -> tuple[float, float] | None:
    if not nums:
        return None
    lo = hi = nums[0]
    for n in nums[1:]:
        if n < lo:
            lo = n
        if n > hi:
            hi = n
    return (lo, hi)


ThresholdsCallable = Callable[[list[float], float, float], int | Sequence[float]]
ThresholdsSpec = int | Sequence[float] | ThresholdsCallable
DomainSpec = Sequence[float] | Callable[[list[float]], Sequence[float]]


@dataclass
class _Binner(Generic[T]):
    _value: Callable[[T], Any]
    _domain: DomainSpec | None
    _thresholds: ThresholdsSpec | None

    def __call__(self, values: Iterable[T]) -> list[Bin[T]]:
        items, nums = _coerce_numbers(values, self._value)
        ex = _extent(nums)
        if ex is None:
            return []
        x0, x1 = ex

        # Domain
        if self._domain is not None:
            dom_spec = self._domain
            if isinstance(dom_spec, Sequence):
                dom = cast(Sequence[float], dom_spec)
            else:
                dom = dom_spec(nums)
            x0, x1 = float(dom[0]), float(dom[1])

        # Thresholds
        thresholds: list[float]
        thr_spec = self._thresholds
        if thr_spec is None:
            k = _sturges(len(nums))
            x0, x1, thresholds = _nice_thresholds_from_count(x0, x1, k)
        elif isinstance(thr_spec, int):
            x0, x1, thresholds = _nice_thresholds_from_count(x0, x1, int(thr_spec))
        elif isinstance(thr_spec, Sequence):
            thresholds = [float(t) for t in cast(Sequence[float], thr_spec)]
        else:
            res = thr_spec(nums, x0, x1)
            if isinstance(res, int):
                x0, x1, thresholds = _nice_thresholds_from_count(x0, x1, int(res))
            else:
                thresholds = [float(t) for t in res]

        thresholds.sort()
        # Keep only interior thresholds.
        thresholds = [t for t in thresholds if x0 < t < x1]

        edges = [x0, *thresholds, x1]
        bins = [Bin[T](edges[i], edges[i + 1]) for i in range(len(edges) - 1)]

        # Assign values. Half-open [x0, x1) except last bin includes x1.
        last = len(bins) - 1
        for item, v in zip(items, nums):
            if v < x0 or v > x1:
                continue
            # find index by thresholds
            i = 0
            j = len(thresholds)
            while i < j:
                m = (i + j) >> 1
                if v < thresholds[m]:
                    j = m
                else:
                    i = m + 1
            idx = i
            if idx == last and v == x1:
                bins[last].append(item)
            else:
                bins[idx].append(item)

        return bins

    @overload
    def value(self) -> Callable[[T], Any]: ...

    @overload
    def value(self, fn: Callable[[T], Any]) -> "_Binner[T]": ...

    def value(self, fn: Callable[[T], Any] | None = None):
        if fn is None:
            return self._value
        self._value = fn
        return self

    @overload
    def domain(self) -> DomainSpec | None: ...

    @overload
    def domain(self, dom: DomainSpec | None) -> "_Binner[T]": ...

    def domain(self, dom: DomainSpec | None = None):
        if dom is None:
            return self._domain
        self._domain = dom
        return self

    @overload
    def thresholds(self) -> ThresholdsSpec | None: ...

    @overload
    def thresholds(self, thr: ThresholdsSpec | None) -> "_Binner[T]": ...

    def thresholds(self, thr: ThresholdsSpec | None = None):
        if thr is None:
            return self._thresholds
        self._thresholds = thr
        return self


def _nice_thresholds_from_count(x0: float, x1: float, count: int) -> tuple[float, float, list[float]]:
    if count <= 0 or x0 == x1:
        return (x0, x1, [])
    step = tickStep(x0, x1, count)
    # `tickStep` is non-None and non-zero for finite x0/x1 and count > 0.
    assert step is not None
    step = abs(step)

    def _r(x: float) -> float:
        digits = max(0, -int(math.floor(math.log10(step))) + 2)
        y = round(x, digits)
        return 0.0 if y == 0.0 else y

    nx0 = math.floor(x0 / step) * step
    nx1 = math.ceil(x1 / step) * step
    # interior edges
    nx0 = _r(nx0)
    nx1 = _r(nx1)
    t = nx0 + step
    out: list[float] = []
    while t < nx1 - 1e-15:
        out.append(_r(t))
        t = _r(t + step)
    return (nx0, nx1, out)


def bin() -> _Binner[Any]:
    """Create a D3-style histogram binner (aka `d3.bin()`).

    The returned object is callable: `bin()(values) -> bins`.
    """

    return _Binner(lambda d: d, None, None)

