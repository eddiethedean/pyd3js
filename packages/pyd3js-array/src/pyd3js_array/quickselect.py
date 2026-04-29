"""D3-compatible `quickselect` (in-place selection)."""

from __future__ import annotations

import math
from collections.abc import Callable, MutableSequence
from typing import TypeVar

from pyd3js_array.ascending import ascending

T = TypeVar("T")


def quickselect(
    array: MutableSequence[T],
    k: int,
    left: int = 0,
    right: int | None = None,
    compare: Callable[[T, T], float | int] | None = None,
) -> MutableSequence[T]:
    """Reorder *array* so that `array[k]` is the k-th smallest element.

    Mirrors `d3.quickselect(array, k[, left, right, compare])`.
    """

    # Port of upstream d3-array quickselect (Floyd-Rivest + partition loop).
    # https://github.com/mourner/quickselect
    n = len(array)
    k = int(math.floor(k))
    left = int(math.floor(max(0, left)))
    if right is None:
        right = n - 1
    right = int(math.floor(min(n - 1, right)))

    if not (left <= k <= right):
        return array

    cmp: Callable[[T, T], float | int]
    cmp = ascending if compare is None else compare

    def swap(i: int, j: int) -> None:
        array[i], array[j] = array[j], array[i]

    while right > left:
        if right - left > 600:
            nn = right - left + 1
            m = k - left + 1
            z = math.log(nn)
            s = 0.5 * math.exp(2 * z / 3)
            sd = (
                0.5 * math.sqrt(z * s * (nn - s) / nn) * (-1 if (m - nn / 2) < 0 else 1)
            )
            new_left = max(left, int(math.floor(k - m * s / nn + sd)))
            new_right = min(right, int(math.floor(k + (nn - m) * s / nn + sd)))
            quickselect(array, k, new_left, new_right, cmp)

        t = array[k]
        i = left
        j = right

        swap(left, k)
        if cmp(array[right], t) > 0:
            swap(left, right)

        while i < j:
            swap(i, j)
            i += 1
            j -= 1
            while cmp(array[i], t) < 0:
                i += 1
            while cmp(array[j], t) > 0:
                j -= 1

        if cmp(array[left], t) == 0:
            swap(left, j)
        else:
            j += 1
            swap(j, right)

        if j <= k:
            left = j + 1
        if k <= j:
            right = j - 1

    return array
