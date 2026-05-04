from __future__ import annotations

from typing import Any

from pyd3js_transition.transition.index import Transition, new_id
from pyd3js_transition.transition.schedule import get, schedule


def transition_transition(self) -> Transition:  # noqa: ANN001
    name = self._name
    id0 = self._id
    id1 = new_id()

    groups = self._groups
    for group in groups:
        for i, node in enumerate(group):
            if node is None:
                continue
            inherit = get(node, id0)
            schedule(
                node,
                name,
                id1,
                i,
                group,
                {
                    "time": inherit["time"] + inherit["delay"] + inherit["duration"],
                    "delay": 0.0,
                    "duration": inherit["duration"],
                    "ease": inherit["ease"],
                },
            )
    return Transition(groups, self._parents, name, id1)

