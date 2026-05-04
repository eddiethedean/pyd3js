from __future__ import annotations

from typing import Any

from pyd3js_transition.transition.tween import tween_value


def _text_constant(value: str):
    def fn(this: Any, *_args: Any) -> None:
        setattr(this, "textContent", value)

    return fn


def _text_function(value):  # noqa: ANN001
    def fn(this: Any, *_args: Any) -> None:
        v = value(this)
        setattr(this, "textContent", "" if v is None else v)

    return fn


def text(self, value: Any = None):  # noqa: ANN001
    if callable(value):
        getter = tween_value(self, "text", value)
        t = self.tween("text", _text_function(getter))
        return t.on(
            "end.text.final",
            lambda this, *_: setattr(
                this,
                "textContent",
                "" if getter(this) is None else str(getter(this)),
            ),
        )
    final = "" if value is None else f"{value}"
    t = self.tween("text", _text_constant(final))
    return t.on("end.text.final", lambda this, *_: setattr(this, "textContent", final))

