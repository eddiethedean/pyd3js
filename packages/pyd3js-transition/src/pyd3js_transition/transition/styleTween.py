from __future__ import annotations

import math
from typing import Any, Callable

from pyd3js_transition.transition._interpolate_call import interpolate_call
from pyd3js_transition.transition._style import style_set

_STYLE_TWEENED_FLAG = "__pyd3js_transition_style_tweened__"


def _style_interpolate(name: str, i: Callable[..., Any], priority: str):
    def fn(this: Any, t: float) -> None:
        val = interpolate_call(i, this, t)
        # Match browser/CSS behavior: invalid computed values (e.g. NaN from
        # number interpolation on non-numeric styles) are ignored.
        if isinstance(val, float) and math.isnan(val):
            return
        if isinstance(val, str) and val.lower() == "nan":
            return
        if hasattr(this, "__dict__"):
            this.__dict__[_STYLE_TWEENED_FLAG] = True
        style_set(this, name, val, priority)

    return fn


def _style_tween(name: str, value: Callable[..., Any], priority: str):
    t0: Callable[[Any, float], Any] | None = None
    i0: Any = object()

    def tween(this: Any, *args: Any) -> Any:
        nonlocal t0, i0
        i = value(this, *args)
        if i is not i0:
            i0 = i
            t0 = None if i is None else _style_interpolate(name, i, priority)
        return t0

    setattr(tween, "_value", value)
    return tween


def styleTween(self, name: Any, value: Any = ..., priority: Any = ""):  # noqa: ANN001, N802
    key = f"style.{str(name)}"
    if value is ...:
        v = self.tween(key)
        return getattr(v, "_value", None) if v is not None else None
    if value is None:
        return self.tween(key, None)
    if not callable(value):
        raise RuntimeError
    pr = "" if priority is None else str(priority)
    return self.tween(key, _style_tween(str(name), value, pr))

