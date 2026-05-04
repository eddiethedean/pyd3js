from __future__ import annotations

from concurrent.futures import Future
from typing import Any

from pyd3js_transition.transition.schedule import set as set_schedule


def end(self) -> Future[None]:  # noqa: ANN001
    """
    Return a Future that resolves when all nodes in this transition end.

    If any node is cancelled or interrupted, the Future completes with exception.
    """

    fut: Future[None] = Future()
    id = self._id
    remaining = self.size()

    if remaining == 0:
        fut.set_result(None)
        return fut

    def reject(this: Any, *_args: Any) -> None:
        if not fut.done():
            fut.set_exception(RuntimeError("transition interrupted"))

    def on_end(this: Any, *_args: Any) -> None:
        nonlocal remaining
        remaining -= 1
        if remaining == 0 and not fut.done():
            fut.set_result(None)

    # Attach listeners via schedule dispatch.
    def each(this: Any, *_args: Any) -> None:
        schedule = set_schedule(this, id)
        on0 = schedule["on"]
        on1 = on0.copy()
        on1.on("cancel.__end", reject)
        on1.on("interrupt.__end", reject)
        on1.on("end.__end", on_end)
        schedule["on"] = on1

    self.each(each)
    return fut

