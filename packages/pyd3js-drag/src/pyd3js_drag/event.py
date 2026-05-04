from __future__ import annotations

from typing import Any


class DragEvent:
    def __init__(
        self,
        type_: str,
        *,
        sourceEvent: Any = None,
        subject: Any = None,
        target: Any = None,
        identifier: Any = None,
        active: int = 0,
        x: float = 0.0,
        y: float = 0.0,
        dx: float = 0.0,
        dy: float = 0.0,
        dispatch: Any = None,
    ) -> None:
        self.type = type_
        self.sourceEvent = sourceEvent
        self.subject = subject
        self.target = target
        self.identifier = identifier
        self.active = active
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self._ = dispatch

    def on(self, typenames: Any, listener: Any = ...):  # noqa: ANN401
        # Mirror d3-drag: delegate to the per-gesture dispatch copy.
        value = (
            self._.on(typenames, listener)
            if listener is not ...
            else self._.on(typenames)
        )
        return self if value is self._ else value
