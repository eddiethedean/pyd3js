"""Synchronous Transition shim for d3-axis: mirrors d3's transition() surface (end-state only)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast, overload

from ._svg import Element
from ._selection import Selection

__all__ = ("Transition",)

_T_UNSET = object()


def _wrap(sub: Selection, owner: Transition | None = None) -> "Transition":
    return Transition(sub, _parent_transition=owner)


class Transition:
    """Wraps a Selection: attr/text/each/... apply immediately (d3: final tick state, no timers)."""

    def __init__(
        self,
        selection: Selection,
        _parent_transition: Transition | None = None,
    ) -> None:
        self._sel = selection
        self._parent = _parent_transition
        # Stub scheduling (d3-transition timing; not used for end-state axis parity)
        self._duration_ms: float | None = None
        self._delay_ms: float | None = None
        self._ease_fn: object | None = None

    def selection(self) -> Selection:
        return self._sel

    @overload
    def transition(self) -> Transition: ...

    @overload
    def transition(self, context: object) -> Transition: ...

    def transition(self, context: object | None = None) -> Transition:  # noqa: ANN401, ANN003
        """`selection.transition(context)`: bind this sub-selection to the parent transition (sync)."""
        if context is None:
            return _wrap(self._sel, owner=self)
        if isinstance(context, Transition):
            return _wrap(self._sel, owner=context)
        return _wrap(self._sel, owner=None)

    def call(self, f: Callable[..., object], *args: object) -> Transition:
        f(self, *args)  # type: ignore[operator, misc, call-arg]
        return self

    def each(self, fn: Callable[..., object]) -> Transition:
        self._sel.each(fn)
        return self

    def select(
        self,
        sel: str | Callable[[object, object, int, list[object | None]], object | None],
    ) -> Transition:
        s = self._sel.select(sel)
        return _wrap(s, owner=self)

    def selectAll(self, sel: str) -> Transition:
        s = self._sel.selectAll(sel)
        return _wrap(s, owner=self)

    def data(
        self,
        value: object | Callable[..., object],
        key: Callable[..., object] | None = None,
    ) -> Transition:
        s = self._sel.data(value, key)  # type: ignore[operator, misc, call-arg, arg-type]
        return _wrap(s, owner=self)

    def enter(self) -> Transition:
        s = self._sel.enter()
        return _wrap(s, owner=self)

    def exit(self) -> Transition:
        s = self._sel.exit()
        return _wrap(s, owner=self)

    def append(self, name: str | Callable[[], Element]) -> Transition:
        s = self._sel.append(name)  # type: ignore[operator, misc, call-arg, arg-type]
        return _wrap(s, owner=self)

    def insert(self, name: str, before: str | None) -> Transition:
        s = self._sel.insert(name, before)
        return _wrap(s, owner=self)

    def merge(self, other: Selection | "Transition") -> Transition:
        o: Any = other._sel if isinstance(other, Transition) else other
        s = self._sel.merge(o)
        return _wrap(s, owner=self)

    def order(self) -> Transition:
        self._sel.order()
        return self

    def filter(
        self,
        match: Callable[[object, object, int, list[object | None]], bool],
    ) -> Transition:
        s = self._sel.filter(match)
        return _wrap(s, owner=self)

    def attr(self, name: str, value: object | None = None) -> str | Transition:
        if value is None:
            return cast(str, self._sel.attr(name))  # type: ignore[operator, return-value, no-any-return, arg-type, call-arg, misc]
        s = self._sel.attr(name, value)
        if isinstance(s, str):  # pragma: no cover
            return s
        return _wrap(s, owner=self)

    def text(self, value: object | None = None) -> str | Transition:
        if value is None:
            return cast(str, self._sel.text())  # type: ignore[operator, return-value, no-any-return, arg-type, call-arg, misc]
        s = self._sel.text(value)  # type: ignore[operator, arg-type, call-arg, misc, assignment]
        if isinstance(s, str):  # pragma: no cover
            return s
        return _wrap(s, owner=self)

    def remove(self) -> Transition:
        self._sel.remove()
        return self

    def duration(self, ms: object = _T_UNSET) -> float | Transition:
        if ms is _T_UNSET:
            return 0.0 if self._duration_ms is None else float(self._duration_ms)
        self._duration_ms = float(cast(Any, ms))
        return self

    def delay(self, ms: object = _T_UNSET) -> float | Transition:
        if ms is _T_UNSET:
            return 0.0 if self._delay_ms is None else float(self._delay_ms)
        self._delay_ms = float(cast(Any, ms))
        return self

    def ease(self, fn: object = _T_UNSET) -> object | Transition:
        if fn is _T_UNSET:
            return self._ease_fn
        self._ease_fn = fn
        return self
