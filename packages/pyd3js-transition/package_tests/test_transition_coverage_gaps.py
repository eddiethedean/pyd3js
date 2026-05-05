from __future__ import annotations

from typing import Any

import pytest

import pyd3js_timer._engine as timer_engine
from pyd3js_selection.selection.index import selection
from pyd3js_transition import interrupt
from pyd3js_transition.transition._style import style_remove, style_set, style_value
from pyd3js_transition.transition.index import Transition, transition as transition_factory
from pyd3js_transition.transition.tween import _tween_function


class Node:
    def __init__(self, parent: Any | None = None) -> None:
        self.parentNode = parent
        self.__data__ = {"x": 1}
        self.attrs: dict[str, str] = {}
        self.style: dict[str, str] = {}
        self.textContent = ""

    def getAttribute(self, name: str) -> str | None:  # noqa: N802
        return self.attrs.get(name)

    def setAttribute(self, name: str, value: str) -> None:  # noqa: N802
        self.attrs[name] = value

    def removeAttribute(self, name: str) -> None:  # noqa: N802
        self.attrs.pop(name, None)


def _with_virtual_time() -> tuple[list[float], Any]:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()

    def step(ms: float) -> None:
        wall[0] += ms
        timer_engine._clear_now()
        timer_engine.timer_flush()
        timer_engine.timer_flush()

    return wall, step


def test_interrupt_skips_none_schedule_entry() -> None:
    n = Node()
    selection([[n]], [None]).transition("x")
    schedules = getattr(n, "__transition__")
    key = next(iter(schedules.keys()))
    schedules[key] = None
    interrupt(n, "x")


def test_delay_duration_ease_varying_zero_arg_factories() -> None:
    wall, step = _with_virtual_time()
    n = Node()
    from pyd3js_ease import easeLinear

    t = selection([[n]], [None]).transition("za").duration(20)
    t.delay(lambda: 3.0).duration(lambda: 8.0).easeVarying(lambda: easeLinear)
    step(1)
    tid = t._id
    assert n.__transition__[tid]["delay"] == 3.0
    assert n.__transition__[tid]["duration"] == 8.0


def test_style_helpers_dom_like_and_none_node() -> None:
    assert style_value(None, "opacity") is None
    style_set(None, "opacity", "1")
    style_remove(None, "opacity")

    class CssStyle:
        def __init__(self) -> None:
            self._props: dict[str, str] = {}

        def getPropertyValue(self, name: str) -> str:
            return self._props.get(name, "")

        def setProperty(self, name: str, value: str, _priority: str = "") -> None:
            self._props[name] = value

        def removeProperty(self, name: str) -> None:
            self._props.pop(name, None)

    class DomEl:
        def __init__(self) -> None:
            self.style = CssStyle()

    el = DomEl()
    assert style_value(el, "missing") is None
    el.style._props["empty"] = ""
    assert style_value(el, "empty") is None
    el.style._props["width"] = "10px"
    assert style_value(el, "width") == "10px"
    style_set(el, "opacity", "0.5")
    assert style_value(el, "opacity") == "0.5"
    style_remove(el, "opacity")
    assert style_value(el, "opacity") is None


def test_delay_duration_getters_and_callable_arity() -> None:
    wall, step = _with_virtual_time()
    n = Node()
    t = selection([[n]], [None]).transition("q")
    assert t.delay() == 0
    assert t.duration() == 250

    def delay_di(d: Any, i: int) -> float:
        return float(d["x"]) + float(i)

    def dur_nodes(_d: Any, _i: int, nodes: list[Any]) -> float:
        return float(len(nodes) * 10)

    t2 = selection([[n]], [None]).transition("r").delay(delay_di).duration(dur_nodes)
    step(1)
    assert n.__transition__[t2._id]["delay"] == 1.0
    assert n.__transition__[t2._id]["duration"] == 10.0


def test_ease_varying_errors_and_factory_arity() -> None:
    wall, step = _with_virtual_time()
    n = Node()
    t = selection([[n]], [None]).transition("ev").duration(10)

    with pytest.raises(RuntimeError):
        t.easeVarying(42)  # type: ignore[arg-type]

    def factory(_this: Any, d: Any, _i: int, _nodes: list[Any]):
        return lambda u: u

    t.easeVarying(factory)
    step(50)


def test_ease_varying_non_callable_inner_raises() -> None:
    _wall, step = _with_virtual_time()
    n = Node()
    t = selection([[n]], [None]).transition("ev2").duration(10)

    def factory_bad(*_a: Any, **_k: Any):
        return 3

    # easeVarying's per-node setup runs immediately inside `.easeVarying(...)`.
    with pytest.raises(RuntimeError):
        t.easeVarying(factory_bad)
    step(1)


def test_transition_selection_helpers_and_empty_end() -> None:
    t = Transition([], [], "x", 1)
    assert t.empty()
    assert t.size() == 0
    assert t.nodes() == []
    assert list(iter(t)) == []
    out: list[Any] = []

    def capture(tr: Any, *_a: Any) -> None:
        out.append(tr)

    assert t.call(capture, 1) is t
    assert out and out[0] is t

    fut = t.end()
    assert fut.done()
    assert fut.result() is None


def test_transition_factory_empty() -> None:
    t = transition_factory()
    assert t.empty()


def test_transition_each_callback_arity_variants() -> None:
    n = Node()
    seen: list[Any] = []

    def four(_this: Any, d: Any, i: int, nodes: list[Any]) -> None:
        seen.append(("four", d, i, len(nodes)))

    def three(d: Any, i: int, nodes: list[Any]) -> None:
        seen.append(("three", d, i, len(nodes)))

    def two(d: Any, i: int) -> None:
        seen.append(("two", d, i))

    def one_this(this: Any) -> None:
        seen.append(("one", this))

    def one_d(d: Any) -> None:
        seen.append(("d", d))

    def zero() -> None:
        seen.append("zero")

    t = selection([[n]], [None]).transition("each")
    (
        t.each(four)
        .each(three)
        .each(two)
        .each(one_this)
        .each(one_d)
        .each(zero)
    )
    assert ("four", n.__data__, 0, 1) in seen
    assert ("three", n.__data__, 0, 1) in seen
    assert ("two", n.__data__, 0) in seen
    assert ("one", n) in seen
    # `lambda d: d` binds to the `fn(this)` arity fallback, so it receives the node.
    assert ("d", n) in seen
    assert "zero" in seen


def test_filter_string_and_callable_arity() -> None:
    n = Node()
    t = selection([[n]], [None]).transition("f").duration(1)

    def wide(this: Any, d: Any, i: int, nodes: list[Any]) -> bool:
        return this is n and i == 0 and len(nodes) == 1

    tf = t.filter(wide)
    assert tf._groups == [[n]]

    def narrow(this: Any) -> bool:
        return this is n

    assert t.filter(narrow)._groups == [[n]]
    assert t.filter(lambda: True)._groups == [[n]]

    t2 = selection([[n, None]], [None, None]).transition("f2").duration(1)
    assert t2.filter(lambda *_a: True)._groups == [[n]]


def test_select_and_select_all_custom_selector_arity() -> None:
    class Inner(Node):
        pass

    parent = Node()
    inner = Inner(parent=parent)
    parent.childNodes = [inner]

    wall, step = _with_virtual_time()
    root = selection([[parent]], [None]).transition("u").duration(10)

    def pick_two(d: Any, i: int) -> Any:
        return parent.childNodes[i] if i == 0 else None

    tr = root.select(pick_two)
    assert tr.node() is inner

    def pick_all(_this: Any, _d: Any, _i: int, _nodes: list[Any]) -> list[Any]:
        return list(parent.childNodes)

    tra = selection([[parent]], [None]).transition("v").duration(10).selectAll(pick_all)
    assert tra.node() is inner
    step(20)


def test_select_child_default_star_and_one_arg_fallback() -> None:
    class Child(Node):
        def querySelectorAll(self, sel: str) -> list[Any]:  # noqa: N802
            return [self] if sel == "*" else []

    parent = Node()
    c = Child(parent)
    parent.childNodes = [c]

    wall, step = _with_virtual_time()
    t = selection([[parent]], [None]).transition("sc2").duration(10)

    def pick_one_arg(child: Any) -> bool:
        return child is c

    assert t.selectChild(pick_one_arg).node() is c
    assert t.selectChild(None).node() is c
    step(5)


def test_select_child_string_and_callable_match() -> None:
    class Child(Node):
        def __init__(self, parent: Any) -> None:
            super().__init__(parent)
            self.tag = "span"

        def querySelectorAll(self, sel: str) -> list[Any]:  # noqa: N802
            return [self] if sel in ("*", "span") else []

    parent = Node()
    c = Child(parent)
    parent.childNodes = [c]

    wall, step = _with_virtual_time()
    t = selection([[parent]], [None]).transition("sc").duration(10)

    def pick(child: Any, *_a: Any) -> bool:
        try:
            return child.tag == "span"
        except Exception:
            return False

    assert t.selectChild(pick).node() is c
    assert t.selectChild("*").node() is c
    step(10)


def test_select_child_miss_paths_cover_returns() -> None:
    wall, step = _with_virtual_time()
    parent = Node()
    parent.childNodes = []
    t = selection([[parent]], [None]).transition("miss").duration(1)
    assert t.selectChild(lambda *_a: False).empty()

    class BareChild(Node):
        pass

    parent2 = Node()
    bc = BareChild(parent2)
    parent2.childNodes = [bc]
    t2 = selection([[parent2]], [None]).transition("miss2").duration(1)
    assert t2.selectChild("span").node() is None
    step(2)


def test_select_children_none_defaults_to_star() -> None:
    class Child(Node):
        def querySelectorAll(self, sel: str) -> list[Any]:  # noqa: N802
            return [self] if sel == "*" else []

    parent = Node()
    c = Child(parent)
    parent.childNodes = [c]
    wall, step = _with_virtual_time()
    t = selection([[parent]], [None]).transition("sch_none").duration(5)
    assert t.selectChildren(None).node() is c
    step(5)


def test_select_children_skips_none_parent() -> None:
    wall, step = _with_virtual_time()
    t = selection([[None]], [None]).transition("sk").duration(1)
    sel = t.selectChildren("*")
    assert sel.empty()
    step(2)


def test_select_children_filtered_selector() -> None:
    class Child(Node):
        def __init__(self, parent: Any) -> None:
            super().__init__(parent)

        def querySelectorAll(self, sel: str) -> list[Any]:  # noqa: N802
            return [self] if sel == "span" else []

    class Parent(Node):
        def querySelectorAll(self, sel: str) -> list[Any]:  # noqa: N802
            return [c for c in self.childNodes if c in c.querySelectorAll(sel)]

    parent = Parent()
    c = Child(parent)
    parent.childNodes = [c]

    wall, step = _with_virtual_time()
    t = selection([[parent]], [None]).transition("sch").duration(10)
    sel = t.selectChildren("span")
    assert sel.node() is c
    step(10)


def test_transition_transition_skips_none_node() -> None:
    wall, step = _with_virtual_time()
    n = Node()
    t_first = selection([[n]], [None]).transition("ch").duration(40)
    t0 = Transition([[None, n]], [None, None], "ch", t_first._id)
    t1 = t0.transition()
    assert t1._id != t_first._id
    step(100)


def test_transition_transition_from_running_transition() -> None:
    wall, step = _with_virtual_time()
    n = Node()
    t = selection([[n]], [None]).transition("chain").duration(30)
    t2 = t.transition()
    assert t2._id != t._id
    step(50)


def test_remove_waits_when_other_transition_active() -> None:
    wall, step = _with_virtual_time()
    n = Node()
    parent = Node()
    n.parentNode = parent
    removed: list[Any] = []

    def remove_child(ch: Any) -> None:
        removed.append(ch)

    parent.removeChild = remove_child  # type: ignore[assignment]

    t_short = selection([[n]], [None]).transition("rm").duration(5).remove()
    selection([[n]], [None]).transition("keep").duration(200)
    step(300)
    assert removed == []


def test_attr_interpolate_dict_set_attribute_branch() -> None:
    from pyd3js_transition.transition.attrTween import _attr_interpolate
    from pyd3js_transition.transition.interpolate import interpolate

    calls: list[tuple[str, str]] = []

    node: dict[str, Any] = {"setAttribute": lambda name, val: calls.append((name, val))}
    tween_fn = _attr_interpolate("foo", interpolate("a", "b"))
    tween_fn(node, 0.5)
    assert calls


def test_attr_ns_interpolate_dict_node_invokes_set_attribute_ns() -> None:
    calls: list[tuple[Any, ...]] = []

    class DictNs(dict[str, Any]):
        pass

    node: DictNs = DictNs(
        getAttribute=lambda name: calls.append(("get", name)) or "0",
        setAttribute=lambda name, val: calls.append(("set", name, val)),
        removeAttribute=lambda name: calls.append(("rm", name)),
        getAttributeNS=lambda space, local: calls.append(("getNS", space, local)) or "0",
        setAttributeNS=lambda space, local, val: calls.append(("setNS", space, local, val)),
        removeAttributeNS=lambda space, local: calls.append(("rmNS", space, local)),
        __dict__={},
    )

    from pyd3js_transition.transition.attrTween import _attr_interpolate_ns
    from pyd3js_transition.transition.interpolate import interpolate

    tween_fn = _attr_interpolate_ns({"space": "http://x", "local": "y"}, interpolate("0", "10"))
    tween_fn(node, 0.5)
    assert any(c[0] == "setNS" for c in calls)


def test_style_tween_nan_branch_and_text_tween_bad_value() -> None:
    wall, step = _with_virtual_time()
    n = Node()

    def to_nan(_this: Any, *_a: Any, **_k: Any):
        return lambda _u: float("nan")

    from pyd3js_transition.transition.styleTween import _style_interpolate

    sty = _style_interpolate("opacity", to_nan(n), "")
    sty(n, 0.5)

    sty_str = _style_interpolate("opacity", lambda this, t: "nan", "")
    sty_str(n, 0.5)

    t = selection([[n]], [None]).transition("tx").duration(10)
    with pytest.raises(RuntimeError):
        t.textTween("nope")  # type: ignore[arg-type]

    step(10)


def test_tween_function_guard_raises() -> None:
    with pytest.raises(RuntimeError):
        _tween_function(1, "n", "not-callable")  # type: ignore[arg-type]


def test_schedule_cancel_older_same_name_when_later_transition_starts_first() -> None:
    """Lower-id transition still SCHEDULED when higher-id _start runs → cancel branch."""
    wall, step = _with_virtual_time()
    n = Node()
    log: list[str] = []
    selection([[n]], [None]).transition("preempt").delay(80).duration(10).on("cancel.pre", lambda *_: log.append("cancel"))
    selection([[n]], [None]).transition("preempt").delay(0).duration(10)
    step(10)
    assert "cancel" in log


def test_schedule_stop_ignores_delattr_failure_when_last_transition_ends() -> None:
    class BlockDel(Node):
        def __delattr__(self, name: str) -> None:
            if name == "__transition__":
                raise RuntimeError("blocked delete")
            super().__delattr__(name)

    wall, step = _with_virtual_time()
    n = BlockDel()
    selection([[n]], [None]).transition("bd").duration(5)
    step(50)
    # Last schedule entry is popped; delattr may fail but transition bookkeeping still clears.
    assert getattr(n, "__transition__") == {}


def test_select_skips_none_entries_in_subgroup() -> None:
    parent = Node()
    wall, step = _with_virtual_time()
    t = selection([[None, parent]], [None, None]).transition("sn").duration(5)
    tr = t.select(lambda *_a: parent)
    assert tr.node() is parent
    step(10)


def test_select_call_value_zero_arg_selector() -> None:
    parent = Node()
    inner = Node(parent=parent)
    wall, step = _with_virtual_time()
    t = selection([[parent]], [None]).transition("sel").duration(10)
    tr = t.select(lambda: inner)
    assert tr.node() is inner
    step(15)


def test_select_all_skips_none_parent_in_group() -> None:
    p = Node()
    ch = Node(p)
    wall, step = _with_virtual_time()
    t = selection([[None, p]], [None, None]).transition("san2").duration(3)
    sub = t.selectAll(lambda this, *_a: [ch] if this is p else [])
    assert sub.node() is ch
    step(10)


def test_select_all_call_value_zero_arg_factory() -> None:
    parent = Node()
    a = Node(parent)
    b = Node(parent)

    wall, step = _with_virtual_time()
    t = selection([[parent]], [None]).transition("saz").duration(5)
    sub = t.selectAll(lambda: [a, b])
    assert sub.size() == 2
    step(10)


def test_select_all_call_value_zero_arg_and_skips_none_child() -> None:
    parent = Node()
    a = Node(parent)
    b = Node(parent)

    def pick(*_a: Any) -> list[Any]:
        return [a, None, b]

    wall, step = _with_virtual_time()
    t = selection([[parent]], [None]).transition("sa").duration(10)
    sub = t.selectAll(pick)
    assert sub.size() == 2
    step(15)


def test_select_skips_copying_data_when_parent_has_no_dict() -> None:
    parent = Node()
    inner = Node(parent)
    parent.child = inner  # type: ignore[attr-defined]
    del parent.__dict__["__data__"]
    assert "__data__" not in parent.__dict__
    wall, step = _with_virtual_time()
    selection([[parent]], [None]).transition("sl").duration(10).select(lambda *_a: inner)
    step(15)


def test_style_helper_dict_branch_reads_css_style_object() -> None:
    """Ensure CSSStyleDeclaration path runs when `style` is not a dict."""
    class Css:
        def __init__(self) -> None:
            self._p: dict[str, str] = {"opacity": "1"}

        def getPropertyValue(self, name: str) -> str:
            return self._p.get(name, "")

    class El:
        def __init__(self) -> None:
            self.style = Css()

    assert style_value(El(), "opacity") == "1"


def test_style_memo_paths_on_second_factory_call() -> None:
    from pyd3js_transition.transition.interpolate import interpolate
    from pyd3js_transition.transition.style import _style_constant, _style_function

    n = Node()
    n.style["opacity"] = "0"
    fc = _style_constant("opacity", interpolate, "1")
    first = fc(n)
    assert first is fc(n)

    def getter(this: Any) -> str:
        return "1"

    ff = _style_function("opacity", interpolate, getter)
    n.style["opacity"] = "0"
    one = ff(n)
    assert one is ff(n)


def test_attr_module_dict_paths_and_memo() -> None:
    from pyd3js_transition.transition.attr import (
        _attr_constant,
        _attr_constant_ns,
        _attr_function,
        _attr_function_ns,
        _get_attr,
        _get_attr_ns,
        _remove_attr,
        _remove_attr_ns,
    )
    from pyd3js_transition.transition.interpolate import interpolate

    ga_calls: list[str] = []
    d_plain: dict[str, Any] = {
        "getAttribute": lambda name: ga_calls.append(name) or "plain",
        "removeAttribute": lambda name: ga_calls.append(f"rm:{name}"),
    }
    assert _get_attr(d_plain, "z") == "plain"
    _remove_attr(d_plain, "z")
    assert "rm:z" in "".join(ga_calls)

    dns_calls: list[str] = []
    d_ns: dict[str, Any] = {
        "getAttributeNS": lambda space, local: dns_calls.append(f"{space}|{local}") or "ns",
        "removeAttributeNS": lambda space, local: dns_calls.append(f"rmns:{space}|{local}"),
    }
    assert _get_attr_ns(d_ns, "http://u", "x") == "ns"
    _remove_attr_ns(d_ns, "http://u", "x")
    assert any("rmns:" in str(c) for c in dns_calls)

    uri = "http://www.w3.org/2000/svg"
    fn_const = _attr_constant("opacity", interpolate, "2")
    root = Node()
    root.attrs["opacity"] = "0"
    assert fn_const(root) is not None
    assert fn_const(root) is fn_const(root)

    fn_cns = _attr_constant_ns({"space": uri, "local": "fill"}, interpolate, "x")
    root2 = Node()
    root2.attrs[f"{uri}|fill"] = "y"
    root2.getAttributeNS = lambda space, local: root2.attrs.get(f"{space}|{local}")  # type: ignore[method-assign]
    assert fn_cns(root2) is not None
    assert fn_cns(root2) is fn_cns(root2)

    af = _attr_function("k", interpolate, lambda _this: "z")
    root3 = Node()
    root3.attrs["k"] = "a"
    g1 = af(root3)
    assert g1 is af(root3)

    rm_log: list[tuple[str, str]] = []

    def _rm_ns(space: str, local: str) -> None:
        rm_log.append((space, local))

    d_rm: dict[str, Any] = {
        "getAttributeNS": lambda _s, _l: "z",
        "removeAttributeNS": _rm_ns,
    }
    af_ns = _attr_function_ns({"space": uri, "local": "fill"}, interpolate, lambda _this: None)
    assert af_ns(d_rm) is None
    assert rm_log


def test_tick_returns_early_when_transition_no_longer_active() -> None:
    wall, step = _with_virtual_time()
    n = Node()

    def factory(_node: Any, _d: Any, _i: int, _grp: list[Any]):
        def interp(this: Any, t: float) -> None:
            if t >= 0.5:
                interrupt(n, "tickearly")

        return interp

    selection([[n]], [None]).transition("tickearly").duration(20).tween("x", factory)
    step(100)

