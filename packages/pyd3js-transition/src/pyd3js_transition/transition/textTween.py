from __future__ import annotations

from typing import Any, Callable


def _text_interpolate(i: Callable[[float], Any]):
    def fn(this: Any, t: float) -> None:
        setattr(this, "textContent", i(t))

    return fn


def _text_tween(value: Callable[..., Any]):
    t0: Callable[[Any, float], Any] | None = None
    i0: Any = object()

    def tween(this: Any, *args: Any) -> Any:
        nonlocal t0, i0
        i = value(this, *args)
        if i is not i0:
            i0 = i
            t0 = None if i is None else _text_interpolate(i)
        return t0

    setattr(tween, "_value", value)
    return tween


def textTween(self, value: Any = ...):  # noqa: ANN001, N802
    key = "text"
    if value is ...:
        v = self.tween(key)
        return getattr(v, "_value", None) if v is not None else None
    if value is None:
        return self.tween(key, None)
    if not callable(value):
        raise RuntimeError
    return self.tween(key, _text_tween(value))

