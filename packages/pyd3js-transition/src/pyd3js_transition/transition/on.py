from __future__ import annotations

from typing import Any

from pyd3js_transition.transition.schedule import get, init, set as set_schedule


def _is_start_only(name: str) -> bool:
    for t in name.strip().split():
        i = t.find(".")
        if i >= 0:
            t = t[:i]
        if t and t != "start":
            return False
    return True


def on(self, name: Any, listener: Any = ...):  # noqa: ANN001
    id = self._id
    nm = str(name)
    if listener is ...:
        return get(self.node(), id)["on"].on(nm)

    def each(this: Any, *_args: Any) -> None:
        schedule = (init if _is_start_only(nm) else set_schedule)(this, id)
        on0 = schedule["on"]
        on1 = on0.copy()
        on1.on(nm, listener)
        schedule["on"] = on1

    return self.each(each)

