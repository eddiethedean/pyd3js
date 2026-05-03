"""No-op stream / callback (d3-geo `noop.js`)."""

from __future__ import annotations

from typing import Any


def noop(*_: Any) -> None:
    return None
