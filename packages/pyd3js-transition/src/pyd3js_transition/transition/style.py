from __future__ import annotations

from typing import Any, Callable

from pyd3js_interpolate import interpolateTransformCss

from pyd3js_transition.transition._style import style_remove, style_set, style_value
from pyd3js_transition.transition.interpolate import interpolate
from pyd3js_transition.transition.schedule import set as set_schedule
from pyd3js_transition.transition.tween import tween_value

from pyd3js_transition.transition.styleTween import _STYLE_TWEENED_FLAG

_UNSET = object()


def _style_null(name: str, interp: Callable[[Any, Any], Callable[[float], Any]]):
    string00: str | None = None
    string10: str | None = None
    interpolate0: Callable[[float], Any] | None = None

    def fn(this: Any, *_args: Any):
        nonlocal string00, string10, interpolate0
        string0 = style_value(this, name)
        style_remove(this, name)
        string1 = style_value(this, name)
        if string0 == string1:
            return None
        if string0 == string00 and string1 == string10:
            return interpolate0
        string00 = string0
        string10 = string1
        interpolate0 = interp(string0, string1)
        return interpolate0

    return fn


def _style_constant(name: str, interp: Callable[[Any, Any], Callable[[float], Any]], value1: Any):
    string00: Any = _UNSET
    string1 = f"{value1}"
    interpolate0: Callable[[float], Any] | None = None

    def fn(this: Any, *_args: Any):
        nonlocal string00, interpolate0
        string0 = style_value(this, name)
        if string0 == string1:
            return None
        if string00 is not _UNSET and string0 == string00:
            return interpolate0
        string00 = string0
        interpolate0 = interp(string0, value1)
        return interpolate0

    return fn


def _style_function(name: str, interp: Callable[[Any, Any], Callable[[float], Any]], value: Callable[[Any], Any]):
    string00: str | None = None
    string10: str | None = None
    interpolate0: Callable[[float], Any] | None = None

    def fn(this: Any, *_args: Any):
        nonlocal string00, string10, interpolate0
        string0 = style_value(this, name)
        value1 = value(this)
        string1 = f"{value1}"
        if value1 is None:
            style_remove(this, name)
            value1 = style_value(this, name)
            string1 = f"{value1}"
        if string0 == string1:
            return None
        if string0 == string00 and string1 == string10:
            return interpolate0
        string00 = string0
        string10 = string1
        interpolate0 = interp(string0, value1)
        return interpolate0

    return fn


def _style_maybe_remove(id: int, name: str):
    key = f"style.{name}"
    event = f"end.{key}"
    remove_fn = None

    def each(this: Any, *_args: Any) -> None:
        nonlocal remove_fn
        schedule = set_schedule(this, id)
        on0 = schedule["on"]
        on1 = on0.copy()
        listener = None if schedule.get("value", {}).get(key) is not None else (remove_fn or (remove_fn := (lambda t, *_: style_remove(t, name))))
        on1.on(event, listener)
        schedule["on"] = on1

    return each


def style(self, name: Any, value: Any = None, priority: Any = ""):  # noqa: ANN001
    n = str(name)
    interp = interpolateTransformCss if n == "transform" else interpolate
    if value is None:
        return (
            self.styleTween(n, _style_null(n, interp))
            .on(f"end.style.{n}", lambda this, *_: style_remove(this, n))
        )
    if callable(value):
        return (
            self.styleTween(n, _style_function(n, interp, tween_value(self, f"style.{n}", value)))
            .each(_style_maybe_remove(self._id, n))
        )
    pr = "" if priority is None else str(priority)
    t = self.styleTween(n, _style_constant(n, interp, value), pr).on(f"end.style.{n}", None)
    # Ensure final value is applied even if tween ticks are skipped.
    def _finalize(this, *_args):  # noqa: ANN001
        if hasattr(this, "__dict__") and not this.__dict__.get(_STYLE_TWEENED_FLAG, False):
            return
        style_set(this, n, value, pr)

    return t.on(f"end.style.final.{n}", _finalize)

