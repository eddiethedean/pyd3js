from __future__ import annotations

from typing import Any


def _remove_function(id: int):
    def fn(this: Any, *_args: Any) -> None:
        parent = getattr(this, "parentNode", None)
        schedules = getattr(this, "__transition__", None) or {}
        for i in list(schedules.keys()):
            if int(i) != id:
                return
        if parent is not None and hasattr(parent, "removeChild"):
            parent.removeChild(this)

    return fn


def remove(self):  # noqa: ANN001
    return self.on("end.remove", _remove_function(self._id))

