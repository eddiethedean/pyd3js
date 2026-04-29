from __future__ import annotations

import random
from typing import Callable


def _i32(n: int) -> int:
    n &= 0xFFFFFFFF
    if n >= 0x80000000:
        return n - 0x100000000
    return n


def lcg(seed: float | int | None = None) -> Callable[[], float]:
    mul = 0x19660D
    inc = 0x3C6EF35F
    eps = 1.0 / 0x100000000
    if seed is None:
        seed = random.random()
    if 0 <= float(seed) < 1:
        state = _i32(int(float(seed) / eps))
    else:
        state = _i32(int(abs(float(seed))))

    def next_() -> float:
        nonlocal state
        state = _i32(mul * state + inc)
        u = state & 0xFFFFFFFF
        return eps * u

    return next_


__all__ = ["lcg"]
