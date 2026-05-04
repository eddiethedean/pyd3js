from __future__ import annotations

from typing import Any

from pyd3js_selection import matcher

from pyd3js_transition.transition.index import Transition


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


def filter(self, match: Any) -> Transition:  # noqa: ANN001
    if not callable(match):
        match = matcher(match)

    groups = self._groups
    subgroups: list[list[Any]] = []
    for group in groups:
        subgroup: list[Any] = []
        for i, node in enumerate(group):
            if node is None:
                continue
            if _call_value(match, node, getattr(node, "__data__", None), i, group):
                subgroup.append(node)
        subgroups.append(subgroup)
    return Transition(subgroups, self._parents, self._name, self._id)

