from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from pyd3js_chord._constant import constant
from pyd3js_chord._math import abs_, cos, epsilon, halfPi, sin
from pyd3js_path import path as _path


def _default_source(d: Any) -> Any:
    return d["source"] if isinstance(d, dict) else d.source  # type: ignore[attr-defined]


def _default_target(d: Any) -> Any:
    return d["target"] if isinstance(d, dict) else d.target  # type: ignore[attr-defined]


def _default_radius(d: Any) -> Any:
    return d["radius"] if isinstance(d, dict) else d.radius  # type: ignore[attr-defined]


def _default_start_angle(d: Any) -> Any:
    return d["startAngle"] if isinstance(d, dict) else d.startAngle  # type: ignore[attr-defined]


def _default_end_angle(d: Any) -> Any:
    return d["endAngle"] if isinstance(d, dict) else d.endAngle  # type: ignore[attr-defined]


def _default_pad_angle(*args: Any) -> float:  # noqa: ARG001
    return 0.0


def _default_arrowhead_radius() -> float:
    return 10.0


class _Ribbon:
    def __init__(self, headRadius: Optional[Callable[..., float]] = None):
        self._source = _default_source
        self._target = _default_target
        self._sourceRadius: Callable[..., float] = _default_radius  # type: ignore[assignment]
        self._targetRadius: Callable[..., float] = _default_radius  # type: ignore[assignment]
        self._startAngle: Callable[..., float] = _default_start_angle  # type: ignore[assignment]
        self._endAngle: Callable[..., float] = _default_end_angle  # type: ignore[assignment]
        self._padAngle: Callable[..., float] = _default_pad_angle
        self._context = None
        self._headRadius = headRadius

    def __call__(self, *args: Any) -> Optional[str]:
        buffer = None
        s = self._source(*args)
        t = self._target(*args)
        ap = self._padAngle(*args) / 2

        argv = list(args)

        argv[0] = s
        sr = float(self._sourceRadius(*argv))
        sa0 = float(self._startAngle(*argv)) - halfPi
        sa1 = float(self._endAngle(*argv)) - halfPi

        argv[0] = t
        tr = float(self._targetRadius(*argv))
        ta0 = float(self._startAngle(*argv)) - halfPi
        ta1 = float(self._endAngle(*argv)) - halfPi

        context = self._context
        if context is None:
            buffer = _path()
            context = buffer

        if ap > epsilon:
            if abs_(sa1 - sa0) > ap * 2 + epsilon:
                if sa1 > sa0:
                    sa0 += ap
                    sa1 -= ap
                else:
                    sa0 -= ap
                    sa1 += ap
            else:
                sa0 = sa1 = (sa0 + sa1) / 2

            if abs_(ta1 - ta0) > ap * 2 + epsilon:
                if ta1 > ta0:
                    ta0 += ap
                    ta1 -= ap
                else:
                    ta0 -= ap
                    ta1 += ap
            else:
                ta0 = ta1 = (ta0 + ta1) / 2

        context.moveTo(sr * cos(sa0), sr * sin(sa0))
        context.arc(0, 0, sr, sa0, sa1)

        if sa0 != ta0 or sa1 != ta1:
            if self._headRadius is not None:
                hr = float(self._headRadius(*args))
                tr2 = tr - hr
                ta2 = (ta0 + ta1) / 2
                context.quadraticCurveTo(0, 0, tr2 * cos(ta0), tr2 * sin(ta0))
                context.lineTo(tr * cos(ta2), tr * sin(ta2))
                context.lineTo(tr2 * cos(ta1), tr2 * sin(ta1))
            else:
                context.quadraticCurveTo(0, 0, tr * cos(ta0), tr * sin(ta0))
                context.arc(0, 0, tr, ta0, ta1)

        context.quadraticCurveTo(0, 0, sr * cos(sa0), sr * sin(sa0))
        context.closePath()

        if buffer is not None:
            self._context = None
            out = str(buffer)
            return out or None
        return None

    def headRadius(self, *args: Any):
        if self._headRadius is None:
            raise AttributeError("headRadius is only available on ribbonArrow()")
        if len(args) == 0:
            return self._headRadius
        (value,) = args
        self._headRadius = value if callable(value) else constant(float(value))
        return self

    def radius(self, *args: Any):
        if len(args) == 0:
            return self._sourceRadius
        (value,) = args
        fn = value if callable(value) else constant(float(value))
        self._sourceRadius = fn
        self._targetRadius = fn
        return self

    def sourceRadius(self, *args: Any):
        if len(args) == 0:
            return self._sourceRadius
        (value,) = args
        self._sourceRadius = value if callable(value) else constant(float(value))
        return self

    def targetRadius(self, *args: Any):
        if len(args) == 0:
            return self._targetRadius
        (value,) = args
        self._targetRadius = value if callable(value) else constant(float(value))
        return self

    def startAngle(self, *args: Any):
        if len(args) == 0:
            return self._startAngle
        (value,) = args
        self._startAngle = value if callable(value) else constant(float(value))
        return self

    def endAngle(self, *args: Any):
        if len(args) == 0:
            return self._endAngle
        (value,) = args
        self._endAngle = value if callable(value) else constant(float(value))
        return self

    def padAngle(self, *args: Any):
        if len(args) == 0:
            return self._padAngle
        (value,) = args
        self._padAngle = value if callable(value) else constant(float(value))
        return self

    def source(self, *args: Any):
        if len(args) == 0:
            return self._source
        (value,) = args
        self._source = value
        return self

    def target(self, *args: Any):
        if len(args) == 0:
            return self._target
        (value,) = args
        self._target = value
        return self

    def context(self, *args: Any):
        if len(args) == 0:
            return self._context
        (value,) = args
        self._context = None if value is None else value
        return self


def ribbon() -> _Ribbon:
    return _Ribbon()


def ribbonArrow() -> _Ribbon:
    return _Ribbon(headRadius=constant(_default_arrowhead_radius()))
