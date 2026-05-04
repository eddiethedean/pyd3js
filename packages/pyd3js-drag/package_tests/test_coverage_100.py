from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast

import pyd3js_drag as d
from pyd3js_dispatch import dispatch
from pyd3js_selection._dom import Document, Element, StyleDeclaration


def test_constant_helper() -> None:
    c = d.drag().filter(False).filter()
    assert callable(c)


def test_drag_internal_default_helpers_dict_and_object_branches() -> None:
    from pyd3js_drag.drag import _coord, _default_touchable

    assert _default_touchable({"ontouchstart": True}) is True
    assert _coord(SimpleNamespace(x=1), "x") == 1.0

    ev = SimpleNamespace(x=1.0, y=2.0)
    b = d.drag()
    assert b._default_subject(None, ev, {"x": 9, "y": 9}) == {"x": 9, "y": 9}  # type: ignore[attr-defined]


def test_noevent_helpers_cover_dict_and_attr_paths() -> None:
    from pyd3js_drag.noevent import noevent, nopropagation

    called = {"p": 0, "s": 0}

    e = {
        "preventDefault": lambda: called.__setitem__("p", called["p"] + 1),
        "stopImmediatePropagation": lambda: called.__setitem__("s", called["s"] + 1),
    }
    noevent(e)
    nopropagation(e)
    assert called == {"p": 1, "s": 2}

    called = {"p": 0, "s": 0}
    e2 = SimpleNamespace(
        preventDefault=lambda: called.__setitem__("p", called["p"] + 1),
        stopImmediatePropagation=lambda: called.__setitem__("s", called["s"] + 1),
    )
    noevent(e2)
    assert called == {"p": 1, "s": 1}

    # None is tolerated
    nopropagation(None)


def test_drag_event_on_delegates_to_dispatch() -> None:
    from pyd3js_drag.event import DragEvent

    disp = dispatch("start")
    ev = DragEvent("start", dispatch=disp)

    def listener(_this, _event, _d):  # noqa: ANN001
        return None

    out = ev.on("start", listener)
    assert out is ev
    assert ev.on("start") is listener


def test_nodrag_branches_onselectstart_and_moz_user_select() -> None:
    from pyd3js_drag.nodrag import dragDisable, dragEnable

    doc = Document()

    # onselectstart branch
    root = doc.documentElement
    setattr(root, "onselectstart", None)
    view = {
        "document": doc,
        "addEventListener": lambda *_a: None,
        "removeEventListener": lambda *_a: None,
    }
    dragDisable(view)
    dragEnable(view, noclick=False)

    # MozUserSelect fallback branch
    root2 = Element(tagName="HTML")
    root2.style = StyleDeclaration()  # type: ignore[assignment]
    doc2 = {"documentElement": root2}
    view2 = {
        "document": doc2,
        "addEventListener": lambda *_a: None,
        "removeEventListener": lambda *_a: None,
    }
    dragDisable(view2)
    dragEnable(view2, noclick=True)


def test_nodrag_non_dict_view_and_clear_exception_and_root_dict_pop() -> None:
    import pyd3js_drag.nodrag as nd

    # non-dict view branch (21, 47)
    doc = Document()
    view_obj = SimpleNamespace(document=doc)
    nd.dragDisable(view_obj)
    nd.dragEnable(view_obj, noclick=False)

    # cover _clear exception swallow (55-56) by forcing select() to raise only inside timer start
    old_timer = nd.threading.Timer
    old_select = nd.s.select

    class ImmediateTimer:
        def __init__(self, _t, fn):  # noqa: ANN001
            self.fn = fn

        def start(self):  # noqa: ANN001
            try:
                sel_mod = cast(Any, nd.s)
                sel_mod.select = lambda _v: (_ for _ in ()).throw(RuntimeError("boom"))
                self.fn()
            finally:
                cast(Any, nd.s).select = old_select

    cast(Any, nd.threading).Timer = ImmediateTimer
    try:
        root = {"style": None, "__noselect": "x"}
        view = {"document": {"documentElement": root}}
        nd.dragEnable(view, noclick=True)
    finally:
        cast(Any, nd.threading).Timer = old_timer


def test_drag_configuration_setters_and_click_distance() -> None:
    b = d.drag()

    assert b.clickDistance() == 0.0
    b.clickDistance(2)
    assert b.clickDistance() == 2.0

    # non-callable setters use constant()
    b.filter(False)
    b.container(Element(tagName="DIV"))
    b.subject({"x": 1, "y": 2})
    b.touchable(False)
    assert callable(b.filter())
    assert callable(b.container())
    assert callable(b.subject())
    assert callable(b.touchable())


def test_touch_paths_and_subject_none_short_circuit() -> None:
    doc = Document()
    node = Element(tagName="DIV")
    # Make default touchable detector truthy for this element.
    setattr(node, "ontouchstart", True)
    doc.body.appendChild(node)
    view = {
        "document": doc,
        "addEventListener": lambda *_a: None,
        "removeEventListener": lambda *_a: None,
    }

    behavior = d.drag()
    seen: list[str] = []

    def started(_this, event, _d):  # noqa: ANN001
        seen.append(event.type)

    behavior.on("start", started)

    import pyd3js_selection as s

    s.select(node).call(behavior)

    # touch gesture
    touch = {"identifier": 1, "clientX": 1, "clientY": 2}
    ev = {
        "view": view,
        "changedTouches": [touch],
        "preventDefault": lambda: None,
        "stopImmediatePropagation": lambda: None,
        "ctrlKey": False,
        "button": 0,
    }

    ons = node.__dict__["__on"]
    ts = [o for o in ons if o["type"] == "touchstart"][0]["listener"]
    tm = [o for o in ons if o["type"] == "touchmove"][0]["listener"]
    te = [o for o in ons if o["type"] == "touchend"][0]["listener"]
    ts(node, ev, None)
    tm(node, ev, None)
    te(node, ev, None)
    assert "start" in seen

    # subject returning None prevents gesture
    behavior2 = d.drag().subject(lambda _this, _event, _d: None)
    s.select(node).call(behavior2)
    ts2 = [o for o in node.__dict__["__on"] if o["type"] == "touchstart"][0]["listener"]
    ts2(node, ev, None)


def test_mouse_down_early_returns_and_touch_filter_false() -> None:
    import pyd3js_selection as s

    doc = Document()
    node = Element(tagName="DIV")
    doc.body.appendChild(node)
    beh = d.drag()
    s.select(node).call(beh)

    # touchending early return (192)
    beh._touchending = True  # type: ignore[attr-defined]
    down = [o for o in node.__dict__["__on"] if o["type"] == "mousedown"][0]["listener"]
    down(node, {"view": None, "clientX": 0, "clientY": 0}, None)
    beh._touchending = None  # type: ignore[attr-defined]

    # filter false early return (194)
    beh.filter(lambda _this, _e, _d=None: False)
    down(node, {"view": None, "clientX": 0, "clientY": 0}, None)

    # beforestart returns None (204)
    beh3 = d.drag().subject(lambda _this, _event, _d: None)
    s.select(node).call(beh3)
    down3 = [o for o in node.__dict__["__on"] if o["type"] == "mousedown"][0][
        "listener"
    ]
    down3(node, {"view": None, "clientX": 0, "clientY": 0}, None)

    # touchstarted filter false (266)
    setattr(node, "ontouchstart", True)
    beh2 = d.drag().filter(lambda _this, _e, _d=None: False)
    s.select(node).call(beh2)
    ts = [o for o in node.__dict__["__on"] if o["type"] == "touchstart"][0]["listener"]
    ts(node, {"changedTouches": [{"identifier": 1}]}, None)
