from __future__ import annotations

from typing import Any, Callable

from pyd3js_selection import namespace

from pyd3js_transition.transition._interpolate_call import interpolate_call

_ATTR_TWEENED_FLAG = "__pyd3js_transition_attr_tweened__"


def _attr_interpolate(name: str, i: Callable[..., Any]):
    def fn(this: Any, t: float) -> None:
        if hasattr(this, "__dict__"):
            this.__dict__[_ATTR_TWEENED_FLAG] = True
        if hasattr(this, "setAttribute"):
            this.setAttribute(name, interpolate_call(i, this, t))
        elif isinstance(this, dict) and callable(this.get("setAttribute")):
            this["setAttribute"](name, interpolate_call(i, this, t))

    return fn


def _attr_interpolate_ns(fullname: dict[str, str], i: Callable[..., Any]):
    def fn(this: Any, t: float) -> None:
        if hasattr(this, "__dict__"):
            this.__dict__[_ATTR_TWEENED_FLAG] = True
        if hasattr(this, "setAttributeNS"):
            this.setAttributeNS(fullname["space"], fullname["local"], interpolate_call(i, this, t))
        elif isinstance(this, dict) and callable(this.get("setAttributeNS")):
            this["setAttributeNS"](fullname["space"], fullname["local"], interpolate_call(i, this, t))

    return fn


def _attr_tween_ns(fullname: dict[str, str], value: Callable[..., Any]):
    t0: Callable[[Any, float], Any] | None = None
    i0: Any = object()

    def tween(this: Any, *args: Any) -> Any:
        nonlocal t0, i0
        i = value(this, *args)
        if i is not i0:
            i0 = i
            t0 = None if i is None else _attr_interpolate_ns(fullname, i)
        return t0

    setattr(tween, "_value", value)
    return tween


def _attr_tween(name: str, value: Callable[..., Any]):
    t0: Callable[[Any, float], Any] | None = None
    i0: Any = object()

    def tween(this: Any, *args: Any) -> Any:
        nonlocal t0, i0
        i = value(this, *args)
        if i is not i0:
            i0 = i
            t0 = None if i is None else _attr_interpolate(name, i)
        return t0

    setattr(tween, "_value", value)
    return tween


def attrTween(self, name: Any, value: Any = ...):  # noqa: ANN001, N802
    key = f"attr.{str(name)}"
    if value is ...:
        v = self.tween(key)
        return getattr(v, "_value", None) if v is not None else None
    if value is None:
        return self.tween(key, None)
    if not callable(value):
        raise RuntimeError
    fullname = namespace(name)
    return self.tween(key, _attr_tween_ns(fullname, value) if isinstance(fullname, dict) else _attr_tween(str(fullname), value))

