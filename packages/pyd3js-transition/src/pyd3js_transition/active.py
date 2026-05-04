from __future__ import annotations

from typing import Any

from pyd3js_transition.transition.index import Transition
from pyd3js_transition.transition.schedule import SCHEDULED


_ROOT = [None]


def active(node: Any, name: Any = None) -> Transition | None:
    schedules = getattr(node, "__transition__", None)
    if not schedules:
        return None
    tname = None if name is None else str(name)
    for i, schedule in list(schedules.items()):
        if schedule["state"] > SCHEDULED and schedule["name"] == tname:
            return Transition([[node]], _ROOT, tname, int(i))
    return None

