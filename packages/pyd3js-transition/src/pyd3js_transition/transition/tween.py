from __future__ import annotations

from typing import Any, Callable

from pyd3js_transition.transition.schedule import get, set as set_schedule

_SENTINEL = object()


def _call_value(fn: Any, this: Any, d: Any, i: int, nodes: list[Any]):  # noqa: ANN401
    # Mirror pyd3js-selection’s flexible callback arity handling.
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


def _tween_remove(id: int, name: str):
    tween0: list[dict[str, Any]] | None = None
    tween1: list[dict[str, Any]] | None = None

    def each(this: Any, *_args: Any) -> None:
        nonlocal tween0, tween1
        schedule = set_schedule(this, id)
        tween = schedule["tween"]
        if tween is not tween0:
            tween1 = tween0 = tween
            for i, t in enumerate(list(tween1)):
                if t["name"] == name:
                    tween1 = list(tween1)
                    tween1.pop(i)
                    break
        schedule["tween"] = tween1

    return each


def _tween_function(id: int, name: str, value: Callable[..., Any]):
    if not callable(value):
        raise RuntimeError
    tween0: list[dict[str, Any]] | None = None
    tween1: list[dict[str, Any]] | None = None

    def each(this: Any, *_args: Any) -> None:
        nonlocal tween0, tween1
        schedule = set_schedule(this, id)
        tween = schedule["tween"]
        if tween is not tween0:
            tween1 = list(tween0 := tween)
            t = {"name": name, "value": value}
            for i, existing in enumerate(tween1):
                if existing["name"] == name:
                    tween1[i] = t
                    break
            else:
                tween1.append(t)
        schedule["tween"] = tween1

    return each


def tween(self, name: Any, value: Any = _SENTINEL):  # noqa: ANN001
    id = self._id
    key = str(name)
    if value is _SENTINEL:
        # get
        tw = get(self.node(), id)["tween"]
        for t in tw:
            if t["name"] == key:
                return t["value"]
        return None
    if value is None:
        return self.each(_tween_remove(id, key))
    # set
    if value is not None and not callable(value):
        raise RuntimeError
    return self.each(_tween_function(id, key, value))


def tween_value(transition, name: str, value: Callable[..., Any]):  # noqa: ANN001
    id = transition._id

    def each(this: Any, d: Any, i: int, nodes: list[Any]):  # noqa: ANN001
        schedule = set_schedule(this, id)
        schedule.setdefault("value", {})[name] = _call_value(value, this, d, i, nodes)

    transition.each(each)

    def getter(node: Any):
        return get(node, id).get("value", {}).get(name)

    return getter

