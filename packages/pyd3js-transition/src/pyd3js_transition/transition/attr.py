from __future__ import annotations

from typing import Any, Callable, cast

from pyd3js_interpolate import interpolateTransformSvg
from pyd3js_selection import namespace

from pyd3js_transition.transition.interpolate import interpolate
from pyd3js_transition.transition.tween import tween_value

from pyd3js_transition.transition.attrTween import _ATTR_TWEENED_FLAG

_UNSET = object()


def _get_attr(node: Any, name: str) -> str | None:
    if isinstance(node, dict) and callable(node.get("getAttribute")):
        return node["getAttribute"](name)
    return node.getAttribute(name) if hasattr(node, "getAttribute") else None


def _get_attr_ns(node: Any, space: str, local: str) -> str | None:
    if isinstance(node, dict) and callable(node.get("getAttributeNS")):
        return node["getAttributeNS"](space, local)
    return node.getAttributeNS(space, local) if hasattr(node, "getAttributeNS") else None


def _remove_attr(node: Any, name: str) -> None:
    if isinstance(node, dict) and callable(node.get("removeAttribute")):
        node["removeAttribute"](name)
    elif hasattr(node, "removeAttribute"):
        node.removeAttribute(name)


def _remove_attr_ns(node: Any, space: str, local: str) -> None:
    if isinstance(node, dict) and callable(node.get("removeAttributeNS")):
        node["removeAttributeNS"](space, local)
    elif hasattr(node, "removeAttributeNS"):
        node.removeAttributeNS(space, local)


def _attr_remove(name: str):
    return lambda this, *_: _remove_attr(this, name)


def _attr_remove_ns(fullname: dict[str, str]):
    return lambda this, *_: _remove_attr_ns(this, fullname["space"], fullname["local"])


def _attr_constant(name: str, i: Callable[[Any, Any], Callable[[float], Any]], value1: Any):
    string00: Any = _UNSET
    string1 = f"{value1}"
    interpolate0: Callable[[float], Any] | None = None

    def fn(this: Any, *_args: Any):
        nonlocal string00, interpolate0
        string0 = _get_attr(this, name)
        if string0 == string1:
            return None
        if string00 is not _UNSET and string0 == string00:
            return interpolate0
        string00 = string0
        interpolate0 = i(string0, value1)
        return interpolate0

    return fn


def _attr_constant_ns(fullname: dict[str, str], i: Callable[[Any, Any], Callable[[float], Any]], value1: Any):
    string00: Any = _UNSET
    string1 = f"{value1}"
    interpolate0: Callable[[float], Any] | None = None

    def fn(this: Any, *_args: Any):
        nonlocal string00, interpolate0
        string0 = _get_attr_ns(this, fullname["space"], fullname["local"])
        if string0 == string1:
            return None
        if string00 is not _UNSET and string0 == string00:
            return interpolate0
        string00 = string0
        interpolate0 = i(string0, value1)
        return interpolate0

    return fn


def _attr_function(name: str, i: Callable[[Any, Any], Callable[[float], Any]], value: Callable[[Any], Any]):
    string00: str | None = None
    string10: str | None = None
    interpolate0: Callable[[float], Any] | None = None

    def fn(this: Any, *_args: Any):
        nonlocal string00, string10, interpolate0
        value1 = value(this)
        if value1 is None:
            _remove_attr(this, name)
            return None
        string0 = _get_attr(this, name)
        string1 = f"{value1}"
        if string0 == string1:
            return None
        if string0 == string00 and string1 == string10:
            return interpolate0
        string00 = string0
        string10 = string1
        interpolate0 = i(string0, value1)
        return interpolate0

    return fn


def _attr_function_ns(fullname: dict[str, str], i: Callable[[Any, Any], Callable[[float], Any]], value: Callable[[Any], Any]):
    string00: str | None = None
    string10: str | None = None
    interpolate0: Callable[[float], Any] | None = None

    def fn(this: Any, *_args: Any):
        nonlocal string00, string10, interpolate0
        value1 = value(this)
        if value1 is None:
            _remove_attr_ns(this, fullname["space"], fullname["local"])
            return None
        string0 = _get_attr_ns(this, fullname["space"], fullname["local"])
        string1 = f"{value1}"
        if string0 == string1:
            return None
        if string0 == string00 and string1 == string10:
            return interpolate0
        string00 = string0
        string10 = string1
        interpolate0 = i(string0, value1)
        return interpolate0

    return fn


def attr(self, name: Any, value: Any = None):  # noqa: ANN001
    fullname = namespace(name)
    interp = interpolateTransformSvg if fullname == "transform" else interpolate
    key = f"attr.{name}"
    v = tween_value(self, key, value) if callable(value) else None
    t = self.attrTween(
        name,
        (
            _attr_function_ns(fullname, interp, cast(Callable[[Any], Any], v))
            if isinstance(fullname, dict)
            else _attr_function(str(fullname), interp, cast(Callable[[Any], Any], v))
        )
        if callable(value)
        else (_attr_remove_ns(fullname) if isinstance(fullname, dict) else _attr_remove(str(fullname)))
        if value is None
        else (_attr_constant_ns(fullname, interp, value) if isinstance(fullname, dict) else _attr_constant(str(fullname), interp, value)),
    )
    # Ensure the final value is applied even if the host scheduler skips tween ticks.
    if value is None:
        return t
    if callable(value):
        return t
    final = str(value)
    if isinstance(fullname, dict):
        def _finalize(this, *_args):  # noqa: ANN001
            if hasattr(this, "__dict__") and not this.__dict__.get(_ATTR_TWEENED_FLAG, False):
                return
            this.setAttributeNS(fullname["space"], fullname["local"], final)

        return t.on(f"end.attr.{name}", _finalize)

    def _finalize(this, *_args):  # noqa: ANN001
        if hasattr(this, "__dict__") and not this.__dict__.get(_ATTR_TWEENED_FLAG, False):
            return
        this.setAttribute(str(fullname), final)

    return t.on(f"end.attr.{name}", _finalize)

