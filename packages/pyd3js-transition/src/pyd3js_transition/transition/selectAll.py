from __future__ import annotations

from typing import Any

from pyd3js_selection import selectorAll

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


def selectAll(self, select: Any) -> Transition:  # noqa: ANN001, N802
    name = self._name
    id = self._id

    if not callable(select):
        select = selectorAll(select)

    subgroups: list[list[Any]] = []
    parents: list[Any] = []
    for group in self._groups:
        for i, node in enumerate(group):
            if node is None:
                continue
            children = list(_call_value(select, node, getattr(node, "__data__", None), i, group) or [])
            inherit = get(node, id)
            for k, child in enumerate(children):
                if child is None:
                    continue
                schedule(child, name, id, k, children, inherit)
            subgroups.append(children)
            parents.append(node)

    return Transition(subgroups, parents, name, id)

