from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class Local:
    _id: str

    def get(self, node: Any):
        return getattr(node, self._id, None)

    def set(self, node: Any, value: Any):
        setattr(node, self._id, value)
        return value

    def remove(self, node: Any):
        if hasattr(node, self._id):
            delattr(node, self._id)

    def toString(self) -> str:
        return self._id


def local() -> Local:
    return Local(f"__d3_local_{uuid.uuid4().hex}__")

