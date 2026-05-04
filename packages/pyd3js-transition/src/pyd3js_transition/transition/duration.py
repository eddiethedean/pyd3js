from __future__ import annotations

from typing import Any

from pyd3js_transition.transition.schedule import get, set as set_schedule


def _call_value(fn: Any, this: Any, d: Any, i: int, nodes: list[Any]):  # noqa: ANN401
    try:
        return fn(this, d, i, nodes)
    except TypeError:
        try:
            return fn(d, i, nodes)
        except TypeError:
            try:
                return fn(d, i)
            except TypeError:
                try:
                    return fn(this)
                except TypeError:
                    try:
                        return fn(d)
                    except TypeError:
                        return fn()


def duration(self, value: Any = ...):  # noqa: ANN001
    id = self._id
    if value is ...:
        return get(self.node(), id)["duration"]
    if callable(value):
        def each(this: Any, d: Any, i: int, nodes: list[Any]):  # noqa: ANN001
            set_schedule(this, id)["duration"] = float(_call_value(value, this, d, i, nodes))
        return self.each(each)
    v = float(value)

    def each(this: Any, *_args: Any) -> None:
        set_schedule(this, id)["duration"] = v

    return self.each(each)

