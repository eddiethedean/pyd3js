from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def constant(x: T) -> Callable[..., T]:
    def _const(*args, **kwargs) -> T:  # noqa: ARG001
        return x

    return _const
