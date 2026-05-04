from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pyd3js_selection as s
from pyd3js_dispatch import dispatch
from pyd3js_dispatch.dispatch import Dispatch

from pyd3js_drag.constant import constant
from pyd3js_drag.event import DragEvent
from pyd3js_drag.noevent import noevent, nopropagation
from pyd3js_drag.nodrag import dragDisable, dragEnable


def _default_filter(event: Any) -> bool:
    ctrl = getattr(event, "ctrlKey", False)
    button = getattr(event, "button", 0)
    if isinstance(event, dict):
        ctrl = bool(event.get("ctrlKey", False))
        button = event.get("button", 0)
    return (not ctrl) and (not button)


def _default_container(this: Any) -> Any:
    return (
        getattr(this, "parentNode", None)
        if not isinstance(this, dict)
        else this.get("parentNode")
    )


def _default_touchable(this: Any) -> bool:
    if isinstance(this, dict):
        return "ontouchstart" in this
    return hasattr(this, "ontouchstart")


def _coord(obj: Any, key: str) -> float:
    if isinstance(obj, dict):
        return float(obj.get(key) or 0.0)
    return float(getattr(obj, key, 0.0) or 0.0)


class DragBehavior:
    def __init__(self) -> None:
        self._filter: Callable[..., Any] = self._default_filter
        self._container: Callable[..., Any] = self._default_container
        self._subject: Callable[..., Any] = self._default_subject
        self._touchable: Callable[..., Any] = self._default_touchable

        self._gestures: dict[Any, Any] = {}
        self._listeners: Dispatch = dispatch("start", "drag", "end")
        self._active = 0
        self._click_distance2 = 0.0

        self._mousedownx = 0.0
        self._mousedowny = 0.0
        self._mousemoving = False
        self._touchending: Any = None

        self._target: Any = None

    # Defaults
    def _default_filter(self, _this: Any, event: Any, _d: Any = None) -> bool:
        return _default_filter(event)

    def _default_container(self, this: Any, _event: Any = None, _d: Any = None) -> Any:
        return _default_container(this)

    def _default_subject(self, _this: Any, event: Any, d: Any = None) -> Any:
        if d is None:
            return {"x": event.x, "y": event.y}
        return d

    def _default_touchable(self, this: Any) -> bool:
        return _default_touchable(this)

    # Application (callable behavior)
    def __call__(self, selection: Any) -> None:
        selection.on(
            "mousedown.drag",
            lambda this, e=None, d=None: self._with_target(
                this, self._mousedowned, e, d
            ),
        )

        selection.filter(lambda this, *_a: bool(self._touchable(this))).on(
            "touchstart.drag",
            lambda this, e=None, d=None: self._with_target(
                this, self._touchstarted, e, d
            ),
        ).on(
            "touchmove.drag",
            lambda this, e=None, d=None: self._with_target(
                this, self._touchmoved, e, d
            ),
        ).on(
            "touchend.drag touchcancel.drag",
            lambda this, e=None, d=None: self._with_target(
                this, self._touchended, e, d
            ),
        )

        selection.style("touch-action", "none").style(
            "-webkit-tap-highlight-color", "rgba(0,0,0,0)"
        )

    def _with_target(
        self,
        this: Any,
        fn: Callable[[Any, Any], None],
        event: Any,
        d: Any,
    ) -> None:
        self._target = this
        fn(event, d)

    def _pointer(self, ev: Any, container: Any) -> list[float]:
        return s.pointer(ev, container)

    def _beforestart(
        self,
        that: Any,
        container: Any,
        event: Any,
        d: Any,
        identifier: Any,
        touch: Any = None,
    ):
        dispatch_copy = self._listeners.copy()
        p = self._pointer(touch or event, container)
        before = DragEvent(
            "beforestart",
            sourceEvent=event,
            target=self,
            identifier=identifier,
            active=self._active,
            x=p[0],
            y=p[1],
            dx=0.0,
            dy=0.0,
            dispatch=dispatch_copy,
        )
        subj = self._subject(that, before, d)
        if subj is None:
            return None

        dx = _coord(subj, "x") - p[0]
        dy = _coord(subj, "y") - p[1]

        def gesture(type_: str, event_: Any, touch_: Any = None) -> None:
            nonlocal p, dx, dy
            p0 = p
            if type_ == "start":
                self._gestures[identifier] = gesture
                n = self._active
                self._active += 1
            elif type_ == "end":
                self._gestures.pop(identifier, None)
                self._active -= 1
                p = self._pointer(touch_ or event_, container)
                n = self._active
            else:
                p = self._pointer(touch_ or event_, container)
                n = self._active

            dispatch_copy.call(
                type_,
                that,
                DragEvent(
                    type_,
                    sourceEvent=event_,
                    subject=subj,
                    target=self,
                    identifier=identifier,
                    active=n,
                    x=p[0] + dx,
                    y=p[1] + dy,
                    dx=p[0] - p0[0],
                    dy=p[1] - p0[1],
                    dispatch=dispatch_copy,
                ),
                d,
            )

        return gesture

    # Mouse gesture
    def _mousedowned(self, event: Any, d: Any = None) -> None:
        if self._touchending:
            return
        if not bool(self._filter(self._target, event, d)):
            return

        view = (
            event.get("view")
            if isinstance(event, dict)
            else getattr(event, "view", None)
        )
        cont = self._container(self._target, event, d)
        gesture = self._beforestart(self._target, cont, event, d, "mouse")
        if gesture is None:
            return

        if view is not None:
            s.select(view).on(
                "mousemove.drag",
                lambda _this, e=None, d0=None: self._mousemoved(e, d0),
                True,
            ).on(
                "mouseup.drag",
                lambda _this, e=None, d0=None: self._mouseupped(e, d0),
                True,
            )
            dragDisable(view)

        nopropagation(event)
        self._mousemoving = False
        self._mousedownx = float(
            event.get("clientX")
            if isinstance(event, dict)
            else getattr(event, "clientX", 0.0)
        )
        self._mousedowny = float(
            event.get("clientY")
            if isinstance(event, dict)
            else getattr(event, "clientY", 0.0)
        )
        self._gestures["mouse"] = gesture
        gesture("start", event)

    def _mousemoved(self, event: Any, _d: Any = None) -> None:
        noevent(event)
        if not self._mousemoving:
            cx = float(
                event.get("clientX")
                if isinstance(event, dict)
                else getattr(event, "clientX", 0.0)
            )
            cy = float(
                event.get("clientY")
                if isinstance(event, dict)
                else getattr(event, "clientY", 0.0)
            )
            dx = cx - self._mousedownx
            dy = cy - self._mousedowny
            self._mousemoving = dx * dx + dy * dy > self._click_distance2
        self._gestures["mouse"]("drag", event)

    def _mouseupped(self, event: Any, _d: Any = None) -> None:
        view = (
            event.get("view")
            if isinstance(event, dict)
            else getattr(event, "view", None)
        )
        if view is not None:
            s.select(view).on("mousemove.drag mouseup.drag", None)
            dragEnable(view, self._mousemoving)
        noevent(event)
        self._gestures["mouse"]("end", event)

    # Touch gesture (minimal)
    def _touchstarted(self, event: Any, d: Any = None) -> None:
        if not bool(self._filter(self._target, event, d)):
            return
        touches = (
            event.get("changedTouches")
            if isinstance(event, dict)
            else getattr(event, "changedTouches", [])
        )
        cont = self._container(self._target, event, d)
        for t in list(touches or []):
            ident = (
                t.get("identifier")
                if isinstance(t, dict)
                else getattr(t, "identifier", None)
            )
            gesture = self._beforestart(self._target, cont, event, d, ident, t)
            if gesture is not None:
                nopropagation(event)
                gesture("start", event, t)

    def _touchmoved(self, event: Any, _d: Any = None) -> None:
        touches = (
            event.get("changedTouches")
            if isinstance(event, dict)
            else getattr(event, "changedTouches", [])
        )
        for t in list(touches or []):
            ident = (
                t.get("identifier")
                if isinstance(t, dict)
                else getattr(t, "identifier", None)
            )
            gesture = self._gestures.get(ident)
            if gesture is not None:
                noevent(event)
                gesture("drag", event, t)

    def _touchended(self, event: Any, _d: Any = None) -> None:
        touches = (
            event.get("changedTouches")
            if isinstance(event, dict)
            else getattr(event, "changedTouches", [])
        )
        self._touchending = True
        for t in list(touches or []):
            ident = (
                t.get("identifier")
                if isinstance(t, dict)
                else getattr(t, "identifier", None)
            )
            gesture = self._gestures.get(ident)
            if gesture is not None:
                nopropagation(event)
                gesture("end", event, t)
        self._touchending = None

    # Configuration
    def filter(self, v: Any = ...):
        if v is ...:
            return self._filter
        self._filter = v if callable(v) else constant(bool(v))
        return self

    def container(self, v: Any = ...):
        if v is ...:
            return self._container
        self._container = v if callable(v) else constant(v)
        return self

    def subject(self, v: Any = ...):
        if v is ...:
            return self._subject
        self._subject = v if callable(v) else constant(v)
        return self

    def touchable(self, v: Any = ...):
        if v is ...:
            return self._touchable
        self._touchable = v if callable(v) else constant(bool(v))
        return self

    def on(self, *args: Any):
        value = self._listeners.on(*args)
        return self if value is self._listeners else value

    def clickDistance(self, v: Any = ...):
        if v is ...:
            return self._click_distance2**0.5
        vv = float(v)
        self._click_distance2 = vv * vv
        return self


def drag() -> DragBehavior:
    return DragBehavior()


__all__ = ["DragBehavior", "drag"]
