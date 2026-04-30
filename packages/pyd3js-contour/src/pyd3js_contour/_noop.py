"""No-op callback (mirrors d3-contour noop.js)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

__all__ = ["noop"]


def noop(*_args: Any, **_kwargs: Any) -> None:
    return None


def noop_factory() -> Callable[..., None]:
    return noop
