from __future__ import annotations

from typing import Any

from pyd3js_transition.transition.index import Transition


def merge(self, other: Any) -> Transition:  # noqa: ANN001
    if other._id != self._id:
        raise RuntimeError

    groups0 = self._groups
    groups1 = other._groups
    m = min(len(groups0), len(groups1))
    merges: list[list[Any]] = []
    for j in range(m):
        g0 = groups0[j]
        g1 = groups1[j]
        merge_group: list[Any] = []
        for i in range(len(g0)):
            node = g0[i] or g1[i]
            merge_group.append(node)
        merges.append(merge_group)
    merges.extend(groups0[m:])
    return Transition(merges, self._parents, self._name, self._id)

