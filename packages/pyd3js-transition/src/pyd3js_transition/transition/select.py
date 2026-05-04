from __future__ import annotations

from typing import Any

from pyd3js_selection import selector

from pyd3js_transition.transition.index import Transition
from pyd3js_transition.transition.schedule import get, schedule


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


def select(self, select: Any) -> Transition:  # noqa: ANN001
    name = self._name
    id = self._id

    if not callable(select):
        select = selector(select)

    groups = self._groups
    subgroups: list[list[Any]] = []
    for group in groups:
        subgroup: list[Any] = [None] * len(group)
        for i, node in enumerate(group):
            if node is None:
                continue
            subnode = _call_value(select, node, getattr(node, "__data__", None), i, group)
            if subnode is None:
                continue
            if hasattr(node, "__dict__") and "__data__" in node.__dict__:
                setattr(subnode, "__data__", getattr(node, "__data__", None))
            subgroup[i] = subnode
            schedule(subnode, name, id, i, subgroup, get(node, id))
        subgroups.append(subgroup)
    return Transition(subgroups, self._parents, name, id)

