from __future__ import annotations

from collections.abc import Callable
from typing import Any

EPS = 1e-6


def assert_in_delta(actual: float, expected: float) -> None:
    assert expected - EPS < actual < expected + EPS, (actual, expected)


def ease_out(ease_in: Callable[[Any], float]) -> Callable[[Any], float]:
    def _out(t: Any) -> float:
        return 1.0 - ease_in(1.0 - t)

    return _out


def ease_in_out(ease_in: Callable[[Any], float]) -> Callable[[Any], float]:
    def _in_out(t: Any) -> float:
        if t < 0.5:
            return ease_in(t * 2) / 2
        return (2 - ease_in((1 - t) * 2)) / 2

    return _in_out
