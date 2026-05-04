from __future__ import annotations

from typing import Any, Callable

from pyd3js_transition.transition.schedule import get, set as set_schedule


def ease(self, value: Any = ...):  # noqa: ANN001
    id = self._id
    if value is ...:
        return get(self.node(), id)["ease"]
    if not callable(value):
        raise RuntimeError

    def each(this: Any, *_args: Any) -> None:
        set_schedule(this, id)["ease"] = value

    return self.each(each)

