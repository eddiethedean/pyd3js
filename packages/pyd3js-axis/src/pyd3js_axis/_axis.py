"""d3-axis `axis(orient, scale)` — full path including transition (synchronous end-state)."""

from __future__ import annotations

import math
from collections.abc import Callable
from typing import Any, cast

from ._constants import BOTTOM, LEFT, RIGHT, TOP
from ._enter import EnterNode
from ._identity import identity
from ._selection import Selection, _as_element
from ._svg import Element

_UNSET = object()
_EPS = 1e-6


def _svg_number(v: float) -> str:
    return format(v, "g")


def _translate_x(x: float | str) -> str:
    return f"translate({x},0)"


def _translate_y(y: float | str) -> str:
    return f"translate(0,{y})"


def _number(scale: Any) -> Callable[[Any], float]:
    return lambda d: float(scale(d))


def _center(scale: Any, offset: float) -> Callable[[Any], float]:
    bw_call = getattr(scale, "bandwidth", None)
    bw = float(bw_call()) if callable(bw_call) else 0.0
    off = max(0.0, bw - offset * 2.0) / 2.0
    rnd = getattr(scale, "round", None)
    if callable(rnd) and bool(rnd()):  # type: ignore[operator, misc, truthy-bool]
        off = float(round(off))
    return lambda d: float(scale(d)) + off


def _invoke_ticks(scale: Any, tick_arguments: list[object]) -> list[object]:
    t = getattr(scale, "ticks", None)
    if callable(t):
        return list(t(*tick_arguments)) if tick_arguments else list(t())
    dom = getattr(scale, "domain", None)
    if callable(dom):
        return list(dom())  # type: ignore[operator, misc]
    return []  # e.g. `ticks` is non-callable and `domain` is missing


def _invoke_tick_format(
    scale: Any, tick_arguments: list[object]
) -> Callable[[Any], str]:
    tf = getattr(scale, "tickFormat", None)
    if not callable(tf):
        return cast(Callable[[Any], str], identity)
    fmt = tf(*tick_arguments) if tick_arguments else tf()
    if fmt is None:
        return cast(Callable[[Any], str], identity)
    return cast(Callable[[Any], str], fmt)


class Axis:
    """Callable axis generator returned by `axisTop` / `axisLeft` / …."""

    def __init__(self, orient: int, scale: Any) -> None:
        self._orient = orient
        self._scale = scale
        self._tick_arguments: list[object] = []
        self._tick_values: list[object] | None = None
        self._tick_format: Callable[..., Any] | None = None
        self._tick_size_inner = 6
        self._tick_size_outer = 6
        self._tick_padding = 3
        self._offset = 0.5

    def __call__(self, context: Any) -> None:  # noqa: ANN401, ANN204
        scale = self._scale
        orient = self._orient
        tick_arguments = self._tick_arguments
        tick_values = self._tick_values
        tick_format = self._tick_format
        tick_size_inner = self._tick_size_inner
        tick_size_outer = self._tick_size_outer
        tick_padding = self._tick_padding
        offset = self._offset

        k = -1 if orient in (TOP, LEFT) else 1
        x = "x" if orient in (LEFT, RIGHT) else "y"
        transform = _translate_x if orient in (TOP, BOTTOM) else _translate_y

        values = (
            list(tick_values)
            if tick_values is not None
            else (
                _invoke_ticks(scale, tick_arguments)
                if getattr(scale, "ticks", None)
                else list(scale.domain())  # type: ignore[union-attr, attr-defined, operator, misc]
            )
        )
        if tick_format is None:
            fmt_call = _invoke_tick_format(scale, tick_arguments)
        else:
            fmt_call = tick_format  # type: ignore[assignment, misc]

        spacing = max(tick_size_inner, 0) + tick_padding
        rng = scale.range()  # type: ignore[union-attr, attr-defined]
        range0 = float(rng[0]) + offset  # type: ignore[arg-type, index, misc]
        range1 = float(rng[-1]) + offset  # type: ignore[arg-type, index, misc]

        if callable(getattr(scale, "bandwidth", None)):
            position = _center(scale.copy(), offset)  # type: ignore[union-attr, attr-defined]
        else:
            position = _number(scale.copy())  # type: ignore[union-attr, attr-defined]

        selection = context.selection() if hasattr(context, "selection") else context
        if not isinstance(selection, Selection):
            raise TypeError(
                "axis(context) expects a Selection (or object with .selection())"
            )

        path: Any = selection.selectAll(".domain").data([None])
        tick: Any = selection.selectAll(".tick").data(values, key=scale).order()  # type: ignore[operator, misc, call-arg]
        tick_exit: Any = tick.exit()
        tick_enter: Any = tick.enter().append("g").attr("class", "tick")
        line: Any = tick.select("line")
        text: Any = tick.select("text")

        path = path.merge(
            path.enter()
            .insert("path", ".tick")
            .attr("class", "domain")
            .attr("stroke", "currentColor")
        )
        tick = tick.merge(tick_enter)

        line = line.merge(
            tick_enter.append("line")
            .attr("stroke", "currentColor")
            .attr(f"{x}2", _svg_number(k * tick_size_inner))
        )
        text = text.merge(
            tick_enter.append("text")
            .attr("fill", "currentColor")
            .attr(x, _svg_number(k * spacing))
            .attr(
                "dy",
                "0em"
                if orient == TOP
                else ("0.71em" if orient == BOTTOM else "0.32em"),
            )
        )

        if context is not selection:
            tr_ctx = context
            path = path.transition(tr_ctx)
            tick = tick.transition(tr_ctx)
            line = line.transition(tr_ctx)
            text = text.transition(tr_ctx)

            def _exit_tfn(
                n: object, d: object, i: int, g: list[object | None]
            ) -> str | None:
                v = position(cast(Any, d))
                if math.isfinite(v):
                    return transform(_svg_number(v + offset))
                el = _as_element(n)
                return el.get_attribute("transform") if el else None

            tick_exit = (
                tick_exit.transition(tr_ctx)
                .attr("opacity", _svg_number(_EPS))
                .attr("transform", _exit_tfn)
            )

            def _enter_tfn(n: object, d: object, i: int, g: list[object | None]) -> str:  # noqa: ARG001
                parent: Element | None
                if isinstance(
                    n, EnterNode
                ):  # pragma: no cover  # join uses post-append `Element` nodes
                    parent = n._parent
                elif isinstance(n, Element) and n.parent is not None:
                    parent = n.parent
                else:  # pragma: no cover
                    parent = None
                p_fn = None
                if parent is not None:
                    p_fn = getattr(parent, "d3__axis", None) or getattr(
                        parent, "__axis", None
                    )
                v_out: float
                if callable(p_fn):
                    try:
                        pv = float(p_fn(d))  # type: ignore[operator, misc, call-arg, truthy-bool]
                    except (TypeError, ValueError):
                        pv = float("nan")
                    if math.isfinite(pv):
                        v_out = pv
                    else:
                        v_out = float(position(cast(Any, d)))
                else:
                    v_out = float(position(cast(Any, d)))
                return transform(_svg_number(v_out + offset))

            tick_enter.attr("opacity", _svg_number(_EPS)).attr("transform", _enter_tfn)

        tick_exit.remove()  # type: ignore[union-attr, misc, operator, attr-defined, truthy-iterable]

        if orient in (LEFT, RIGHT):
            d_path = (
                f"M{_svg_number(k * tick_size_outer)},{_svg_number(range0)}H{_svg_number(offset)}"
                f"V{_svg_number(range1)}H{_svg_number(k * tick_size_outer)}"
                if tick_size_outer
                else f"M{_svg_number(offset)},{_svg_number(range0)}V{_svg_number(range1)}"
            )
        else:
            d_path = (
                f"M{_svg_number(range0)},{_svg_number(k * tick_size_outer)}V{_svg_number(offset)}"
                f"H{_svg_number(range1)}V{_svg_number(k * tick_size_outer)}"
                if tick_size_outer
                else f"M{_svg_number(range0)},{_svg_number(offset)}H{_svg_number(range1)}"
            )
        path.attr("d", d_path)  # type: ignore[union-attr, misc, operator, attr-defined, call-arg, truthy-iterable, truthy-bool, assignment]

        def _tf(
            _n: object, d: object, _i: int, _g: list[object | None]
        ) -> str:
            return str(fmt_call(d))  # type: ignore[operator, misc, call-arg]

        tick.attr("opacity", 1).attr(
            "transform",
            lambda _n, d, _i, _g: transform(
                _svg_number(float(position(cast(Any, d))) + offset)
            ),
        )
        line.attr(f"{x}2", _svg_number(k * tick_size_inner))
        text.attr(x, _svg_number(k * spacing)).text(_tf)

        def _entering(
            node: object, _d: object, _i: int, _g: list[object | None]
        ) -> bool:
            return getattr(node, "d3__axis", None) is None

        selection.filter(_entering).attr("fill", "none").attr("font-size", 10).attr(
            "font-family", "sans-serif"
        ).attr(
            "text-anchor",
            "start" if orient == RIGHT else ("end" if orient == LEFT else "middle"),
        )

        def _stash(n: object, _d: object, _i: int, _g: list[object | None]) -> None:
            if isinstance(n, Element):
                n.d3__axis = position
                n.__axis = position  # d3: this.__axis in axis.js

        selection.each(_stash)

    def scale(self, arg: Any = _UNSET) -> Any:  # noqa: ANN401, ANN003
        if arg is _UNSET:
            return self._scale
        self._scale = arg
        return self

    def ticks(self, *args: object) -> "Axis":
        self._tick_arguments = list(args)
        return self

    def tickArguments(self, arg: Any = _UNSET) -> list[object] | "Axis":  # noqa: ANN401, N802
        if arg is _UNSET:
            return list(self._tick_arguments)
        self._tick_arguments = [] if arg is None else list(arg)  # type: ignore[arg-type, misc]
        return self

    def tickValues(self, arg: Any = _UNSET) -> list[object] | None | "Axis":  # noqa: ANN401, N802
        if arg is _UNSET:
            return list(self._tick_values) if self._tick_values is not None else None
        self._tick_values = None if arg is None else list(arg)  # type: ignore[arg-type, misc]
        return self

    def tickFormat(self, arg: Any = _UNSET) -> Any | "Axis":  # noqa: ANN401, N802
        if arg is _UNSET:
            return self._tick_format
        self._tick_format = arg
        return self

    def tickSize(self, arg: Any = _UNSET) -> float | "Axis":  # noqa: ANN401, N802
        if arg is _UNSET:
            return float(self._tick_size_inner)
        v = float(arg)
        self._tick_size_inner = v
        self._tick_size_outer = v
        return self

    def tickSizeInner(self, arg: Any = _UNSET) -> float | "Axis":  # noqa: ANN401, N802
        if arg is _UNSET:
            return float(self._tick_size_inner)
        self._tick_size_inner = float(arg)
        return self

    def tickSizeOuter(self, arg: Any = _UNSET) -> float | "Axis":  # noqa: ANN401, N802
        if arg is _UNSET:
            return float(self._tick_size_outer)
        self._tick_size_outer = float(arg)
        return self

    def tickPadding(self, arg: Any = _UNSET) -> float | "Axis":  # noqa: ANN401, N802
        if arg is _UNSET:
            return float(self._tick_padding)
        self._tick_padding = float(arg)
        return self

    def offset(self, arg: Any = _UNSET) -> float | "Axis":  # noqa: ANN401, N802
        if arg is _UNSET:
            return float(self._offset)
        self._offset = float(arg)
        return self


def axis_top(scale: Any) -> Axis:  # noqa: ANN401, ANN003
    return Axis(TOP, scale)


def axis_right(scale: Any) -> Axis:  # noqa: ANN401, ANN003
    return Axis(RIGHT, scale)


def axis_bottom(scale: Any) -> Axis:  # noqa: ANN401, ANN003
    return Axis(BOTTOM, scale)


def axis_left(scale: Any) -> Axis:  # noqa: ANN401, ANN003
    return Axis(LEFT, scale)
