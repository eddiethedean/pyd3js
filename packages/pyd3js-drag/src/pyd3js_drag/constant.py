from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def constant(x: T) -> Callable[[], T]:
    return lambda: x
