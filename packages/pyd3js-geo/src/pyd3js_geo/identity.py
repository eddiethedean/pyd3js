"""Identity stream / transform (d3-geo `identity.js` / pass-through)."""

from __future__ import annotations

from typing import Any


def identity(stream: Any) -> Any:
    return stream
