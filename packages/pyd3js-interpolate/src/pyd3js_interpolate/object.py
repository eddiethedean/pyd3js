"""interpolateObject — port of d3-interpolate `object.js`."""

from __future__ import annotations

import inspect
from collections.abc import Callable, Mapping
from typing import Any


def _object_as_dict(o: Any) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for cls in reversed(type(o).__mro__[:-1]):
        for k, v in cls.__dict__.items():
            if k.startswith("_"):
                continue
            if isinstance(v, (classmethod, staticmethod)):
                continue
            if callable(v) and not isinstance(v, type):
                continue
            try:
                merged[k] = getattr(o, k)
            except AttributeError:
                pass
    od = getattr(o, "__dict__", None)
    if od:
        merged.update({k: v for k, v in od.items() if not str(k).startswith("_")})
    for name in ("valueOf", "toString"):
        for cls in type(o).__mro__[:-1]:
            if name in cls.__dict__:
                m = getattr(o, name, None)
                if callable(m) and name not in merged:
                    merged[name] = m
                break
    return merged


def _normalize_object(a: Any) -> dict[str, Any]:
    if a is None:
        return {}
    if isinstance(a, dict):
        return dict(a)
    if isinstance(a, Mapping) and not isinstance(a, (str, bytes)):
        return dict(a)
    if isinstance(a, (bool, int, float, str, bytes)):
        return {}
    # object.js: typeof x !== "object" (functions, classes) → {} for key iteration
    if isinstance(a, type) or inspect.isroutine(a):
        return {}
    return _object_as_dict(a)


def interpolate_object(a: Any, b: Any) -> Callable[[float], dict[str, Any]]:
    from pyd3js_interpolate.value import interpolate_value

    a_d = _normalize_object(a)
    b_d = _normalize_object(b)
    interpolators = {k: interpolate_value(a_d[k], b_d[k]) for k in b_d if k in a_d}
    constants = {k: b_d[k] for k in b_d if k not in interpolators}

    def f(t: float) -> dict[str, Any]:
        out = dict(constants)
        for k, itp in interpolators.items():
            out[k] = itp(t)
        return out

    return f


__all__ = ["interpolate_object", "_object_as_dict", "_normalize_object"]
