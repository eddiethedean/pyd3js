from __future__ import annotations

from typing import Any

from pyd3js_ease import easeCubicInOut
from pyd3js_timer import now

from pyd3js_transition.transition.index import Transition, new_id
from pyd3js_transition.transition.schedule import schedule


_DEFAULT_TIMING: dict[str, Any] = {
    "time": None,
    "delay": 0.0,
    "duration": 250.0,
    "ease": easeCubicInOut,
}


def _inherit_timing(node: Any, transition_id: int) -> dict[str, Any]:
    while True:
        schedules = getattr(node, "__transition", None) or getattr(node, "__transition__", None)
        if schedules and transition_id in schedules:
            return schedules[transition_id]
        parent = getattr(node, "parentNode", None)
        if parent is None:
            raise RuntimeError(f"transition {transition_id} not found")
        node = parent


def selection_transition(self, name: Any = None):  # noqa: ANN001
    # Port of d3-transition selection/transition.js
    timing: dict[str, Any] | None
    if isinstance(name, Transition):
        transition_id = name._id
        tname = name._name
        timing = None
    else:
        transition_id = new_id()
        _DEFAULT_TIMING["time"] = now()
        tname = None if name is None else str(name)
        timing = _DEFAULT_TIMING

    groups = self._groups
    for group in groups:
        for i, node in enumerate(group):
            if node is None:
                continue
            schedule(node, tname, transition_id, i, group, timing or _inherit_timing(node, transition_id))

    return Transition(groups, self._parents, tname, transition_id)

