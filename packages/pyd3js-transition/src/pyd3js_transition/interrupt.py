from __future__ import annotations

from typing import Any

from pyd3js_transition._schedules import schedules_get, schedules_try_del
from pyd3js_transition.transition.schedule import ENDING, ENDED, STARTING


def interrupt(node: Any, name: Any = None) -> None:
    schedules = schedules_get(node)
    if not schedules:
        return

    tname = None if name is None else str(name)
    empty = True

    # Copy keys because callbacks delete schedules.
    for i in list(schedules.keys()):
        schedule = schedules.get(i)
        if schedule is None:
            continue
        if schedule["name"] != tname:
            empty = False
            continue
        active = schedule["state"] > STARTING and schedule["state"] < ENDING
        schedule["state"] = ENDED
        schedule["timer"].stop()
        schedule["on"].call("interrupt" if active else "cancel", node, getattr(node, "__data__", None), schedule["index"], schedule["group"])
        schedules.pop(i, None)

    if empty:
        schedules_try_del(node)

