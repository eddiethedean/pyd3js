from __future__ import annotations

from typing import Any

import pyd3js_selection as s
import pyd3js_selection._globals as g
from pyd3js_selection._dom import Element, parse_html
from pyd3js_selection.selection.index import EnterNode, selection


def test_call_value_fallbacks_hit_all_arity_paths() -> None:
    # Force _call_value to fall through to fn()
    called = {"n": 0}

    def f0():  # noqa: ANN001
        called["n"] += 1

    selection([[Element(tagName="DIV")]], [None]).each(f0)
    assert called["n"] == 1

    # Force _call_value to call fn(this) as last resort
    called = {"this": None}

    def f1(this):  # noqa: ANN001
        called["this"] = this
        return "ok"

    sel = selection([[Element(tagName="DIV")]], [None])
    sel.each(f1)
    assert called["this"] is sel.node()


def test_selection_root_when_document_is_none() -> None:
    old = g.document
    try:
        g.document = None
        sel = selection()
        assert sel.node() is None
    finally:
        g.document = old


def test_datum_getter_branches_for_object_and_dict() -> None:
    el = Element(tagName="DIV")
    el.__dict__["__data__"] = "x"
    assert selection([[el]], [None]).datum() == "x"

    d = {"__data__": "y"}
    assert selection([[d]], [None]).datum() == "y"

    # node() is None branch
    assert selection([[None]], [None]).datum() is None


def test_datum_set_callable_clears_dict_and_object_branches() -> None:
    el = Element(tagName="DIV")
    el.__dict__["__data__"] = "x"
    d = {"__data__": "y"}

    def clear(_this):  # noqa: ANN001
        return None

    selection([[el, d]], [None]).datum(clear)
    assert "__data__" not in el.__dict__
    assert "__data__" not in d


def test_datum_set_none_deletes_object_dict_and_getattr_fallback() -> None:
    class Obj:
        pass

    o = Obj()
    o.__data__ = 1  # type: ignore[attr-defined]
    d = {"__data__": 2}
    selection([[o, d]], [None]).datum(None)
    assert not hasattr(o, "__data__")
    assert "__data__" not in d

    # getattr fallback branch when "__data__" not in __dict__
    o2 = Obj()
    assert selection([[o2]], [None]).datum() is None


def test_property_getter_checked_default_and_set_delete() -> None:
    class NoChecked:
        pass

    n = NoChecked()
    assert selection([[n]], [None]).property("checked") is False
    assert selection([[{"k": 1}]], [None]).property("k") == 1

    n2 = NoChecked()
    n2.foo = "bar"  # type: ignore[attr-defined]
    selection([[n2]], [None]).property("foo", None)
    assert not hasattr(n2, "foo")


def test_property_callable_setter_and_none_node_skip() -> None:
    el = Element(tagName="DIV")
    el.__dict__["__data__"] = 3
    sel = selection([[el, None]], [None])

    def pv(this, d, i, nodes):  # noqa: ANN001
        return None if i == 0 else "x"

    sel.property("bar", pv)
    assert not hasattr(el, "bar")


def test_filter_string_missing_and_star_paths() -> None:
    doc = parse_html("<div><p></p></div>")
    div = doc.querySelector("div")
    p = doc.querySelector("p")
    assert selection([[None]], [None]).filter("p").size() == 0
    assert selection([[p]], [div]).filter("*").size() == 1


def test_merge_reuse_group_when_other_shorter_and_sort_default_compare() -> None:
    a = Element(tagName="A")
    b = Element(tagName="B")
    s1 = selection([[a], [b]], [None, None])
    s2 = selection([[None]], [None])
    merged = s1.merge(s2)
    assert merged._groups[1] == [b]

    a.__dict__["__data__"] = 2
    b.__dict__["__data__"] = 1
    out = selection([[a, b]], [None]).sort()
    assert [n.tagName for n in out.nodes()] == ["B", "A"]


def test_enter_append_and_insert_paths() -> None:
    doc = parse_html("<div id='p'></div><hr>")
    g.document = doc
    parent = doc.querySelector("#p")

    # Create update selection with no existing <p>, keyed join produces enter nodes.
    upd = s.select(parent).selectAll("p").data([1, 2], lambda d, i=None, nodes=None: d)
    ent = upd.enter()
    out = ent.append("p")
    assert out.size() == 2

    # Enter insert with selector (before hr) and null.
    ent2 = (
        s.select(doc.body)
        .selectAll("p")
        .data([3], lambda d, i=None, nodes=None: d)
        .enter()
    )
    ent2.insert("p", "hr")
    ent2.insert("p", None)


def test_on_branches_non_dict_no_dict_and_remove_event_listener_failure() -> None:
    class Weird:
        def __getattr__(self, name):  # noqa: ANN001
            # hasattr() should not explode, but getattr("__on") should.
            if name == "__on":
                raise RuntimeError("boom")
            raise AttributeError(name)

    w = Weird()
    sel = selection([[w]], [None])
    # add path creates __on via exception branch
    sel.on("click.foo", lambda this, e=None, d=None: None, True)
    # remove path tries removeEventListener and swallows exception
    w.removeEventListener = lambda *_args, **_kwargs: (_ for _ in ()).throw(
        RuntimeError("x")
    )  # type: ignore[attr-defined]
    sel.on("click.foo", None, True)

    # getter when node is None
    assert selection([[None]], [None]).on("click") is None


def test_on_noop_when_only_namespace_given() -> None:
    el = Element(tagName="DIV")
    sel = selection([[el]], [None])
    # on(".name", fn) should be a no-op
    sel.on(".x", lambda *_args: None)
    assert el.__dict__.get("__on") is None


def test_on_slots_object_creates_on_via_getattr_branch_and_add_event_listener_branch() -> (
    None
):
    class Slots:
        __slots__ = ("store", "called")

        def __init__(self) -> None:
            self.store = {}
            self.called = 0

        def __getattr__(self, name):  # noqa: ANN001
            if name == "__on":
                if "__on" not in self.store:
                    raise AttributeError(name)
                return self.store.get("__on")
            raise AttributeError(name)

        def __setattr__(self, name, value):  # noqa: ANN001
            if name == "__on":
                self.store["__on"] = value
                return
            super().__setattr__(name, value)

        def addEventListener(self, *_args, **_kwargs):  # noqa: ANN001
            self.called += 1

    n = Slots()
    sel = selection([[n]], [None])
    sel.on("click.x", lambda *_args: None)
    assert isinstance(n.__on, list)
    assert n.called == 1

    # removal branch for typ + no name (removes unnamed only)
    sel.on("click", lambda *_args: None)
    sel.on("click", None)


def test_on_getter_and_not_list_storage_branches() -> None:
    el = Element(tagName="DIV")
    sel = selection([[el]], [None])
    assert sel.on("click") is None
    sel.on("click", lambda *_args: "unnamed")
    assert callable(sel.on("click"))
    sel.on("click.ns", lambda *_args: "named")
    assert callable(sel.on("click.ns"))

    # __on not list => getter returns None
    el.__dict__["__on"] = {}  # type: ignore[assignment]
    assert sel.on("click") is None


def test_dispatch_listener_fallbacks() -> None:
    el = Element(tagName="DIV")
    sel = selection([[el]], [None])

    # register a listener expecting (e, d)
    seen = {"d": None}

    def l2(e, d):  # noqa: ANN001
        seen["d"] = d

    sel.on("bang", l2)
    el.__dict__["__data__"] = 7
    sel.dispatch("bang")
    assert seen["d"] == 7

    # listener expecting ()
    called = {"n": 0}

    def l0(e):  # noqa: ANN001
        assert e.type == "tick"
        called["n"] += 1

    sel.on("tick.foo", l0)
    sel.dispatch("tick")
    assert called["n"] == 1


def test_remove_value_error_branch() -> None:
    p = Element(tagName="DIV")
    c = Element(tagName="SPAN")
    p.appendChild(c)
    sel = selection([[c]], [None])
    sel.remove()
    # second remove: parent.removeChild will raise ValueError from list.remove
    sel.remove()


def test_dom_insert_before_noop_and_whitespace_data() -> None:
    doc = parse_html("<div><span id='a'></span><span id='b'></span></div>")
    div = doc.querySelector("div")
    a = doc.querySelector("#a")
    b = doc.querySelector("#b")
    # already before: no-op early return branch
    div.insertBefore(a, b)

    # whitespace handle_data branch exercised by parsing with spaces only
    parse_html("   ")


def test_data_keyed_sets_next_pointer() -> None:
    parent = Element(tagName="DIV")
    n1 = Element(tagName="P")
    n1.__dict__["__data__"] = 1
    parent.appendChild(n1)
    # keyed join where first datum is enter followed by update sets enter._next
    sel = selection([[n1]], [parent]).data([0, 1], lambda this, d, i, nodes: d)
    ent = sel.enter()._groups[0][0]
    assert isinstance(ent, EnterNode)
    assert ent._next is sel._groups[0][1]


def test_dom_misc_branches_append_move_next_sibling_and_text_content_children() -> None:
    p1 = Element(tagName="DIV")
    p2 = Element(tagName="DIV")
    c = Element(tagName="SPAN")
    p1.appendChild(c)
    # move semantics branch (remove from old parent)
    p2.appendChild(c)
    assert c.parentNode is p2

    # insertBefore move-from-other-parent branch
    p3 = Element(tagName="DIV")
    p3.insertBefore(c, None)
    assert c.parentNode is p3

    # insertBefore child_at < insert_at decrement branch
    a = Element(tagName="A")
    b = Element(tagName="B")
    c2 = Element(tagName="C")
    p4 = Element(tagName="DIV")
    p4.appendChild(a)
    p4.appendChild(b)
    p4.appendChild(c2)
    # Corrupt parentNode to bypass the "already in right place" early-return,
    # so we can exercise the insert_at decrement path.
    a.parentNode = None
    p4.insertBefore(a, c2)
    assert [x.tagName for x in p4.childNodes] == ["B", "A", "C"]

    # nextSibling parentNode None + ValueError path
    orphan = Element(tagName="X")
    assert orphan.nextSibling is None
    p4._children.remove(b)  # corrupt the list so index() fails
    b.parentNode = p4
    assert b.nextSibling is None

    # textContent branch when children exist
    host = Element(tagName="DIV")
    t = Element(tagName="T")
    t.textContent = "hi"
    host.appendChild(t)
    assert host.textContent == "hi"


def test_dom_namespaced_attributes_and_inner_html_storage_and_empty_selector() -> None:
    el = Element(tagName="DIV")
    el.setAttributeNS("u", "x", "y")
    assert el.getAttributeNS("u", "x") == "y"
    el.removeAttributeNS("u", "x")
    assert el.getAttributeNS("u", "x") is None

    # innerHTML setter/getter path when no children
    el.innerHTML = "<p>hi</p>"
    assert el.innerHTML == "<p>hi</p>"

    # innerHTML should skip namespaced attrs
    c = Element(tagName="P")
    c.setAttribute("id", "a")
    c.setAttribute("u:x", "y")
    el.appendChild(c)
    assert 'u:x="y"' not in el.innerHTML

    assert el.querySelector("") is None
    # empty selector branch in _matches_selector
    assert el.querySelectorAll("") == []


def test_dom_pseudo_class_missing_parent_and_attr_presence_selector() -> None:
    # last-child / first-child with no parentNode branches
    orphan = Element(tagName="DIV")
    # selector becomes "" after stripping pseudo-class
    assert orphan.querySelectorAll(":last-child") == []
    assert orphan.querySelectorAll(":first-child") == []
    assert orphan.querySelectorAll("*:last-child") == []
    assert orphan.querySelectorAll("*:first-child") == []

    # [attr] presence selector branch
    el = Element(tagName="DIV")
    el.setAttribute("data-x", "1")
    assert el.querySelectorAll("[data-x]") == [el]

    # '*' selector branch
    assert el.querySelectorAll("*") == [el]

    # boolean attribute with None value hits handle_starttag v is None branch
    parse_html("<div disabled></div>")


def test_dom_html_serializes_nested_children_branch() -> None:
    root = Element(tagName="DIV")
    c = Element(tagName="SPAN")
    g = Element(tagName="EM")
    c.appendChild(g)
    root.appendChild(c)
    assert root.innerHTML == "<span><em></em></span>"


def test_dispatch_params_callable_and_on_dict_storage_fallbacks() -> None:
    dnode: dict = {}
    sel = selection([[dnode]], [None])

    got = {"detail": None}

    def listener(this, e, d):  # noqa: ANN001
        got["detail"] = e.detail

    # force dict storage for __on and dict-branch in dispatch() for __data__
    sel.on("boom", listener)
    dnode["__data__"] = 5

    def params(this, d, i, nodes):  # noqa: ANN001
        return {"detail": {"d": d, "i": i}, "bubbles": True, "cancelable": True}

    sel.dispatch("boom", params)
    assert got["detail"] == {"d": 5, "i": 0}

    # __on not list branch
    dnode["__on"] = {}  # type: ignore[assignment]
    sel.dispatch("boom")


def test_enter_exit_when_unset() -> None:
    sel = selection([[Element(tagName="DIV")]], [None])
    assert sel.enter().size() == 0
    assert sel.exit().size() == 0


def test_text_html_callable_setters_skip_none_nodes() -> None:
    a = Element(tagName="DIV")
    b = Element(tagName="DIV")
    a.__dict__["__data__"] = "x"
    b.__dict__["__data__"] = "y"

    sel = selection([[a, None, b]], [None])

    def tv(this, d, i, nodes):  # noqa: ANN001
        return f"{d}-{i}"

    sel.text(tv)
    assert a.textContent == "x-0"
    assert b.textContent == "y-2"

    def hv(this, d, i, nodes):  # noqa: ANN001
        return f"<b>{d}</b>"

    sel.html(hv)
    assert a.innerHTML == "<b>x</b>"
    assert b.innerHTML == "<b>y</b>"


def test_select_and_select_all_none_selector_paths() -> None:
    el = Element(tagName="DIV")
    sel = selection([[el]], [None])
    assert sel.select(None).node() is None
    assert sel.selectAll(None).size() == 0


def test_data_keyed_skips_none_nodes_and_marks_exit_nodes() -> None:
    parent = Element(tagName="DIV")
    n1 = Element(tagName="P")
    n1.__dict__["__data__"] = "k1"
    parent.appendChild(n1)
    # group includes None to hit keyed join skip branch
    sel = selection([[None, n1]], [parent]).data(
        ["k1", "k2"], lambda this, d, i, nodes: d
    )
    # exit group exists and length matches original group
    assert len(sel.exit()._groups[0]) == 2


def test_index_misc_missing_branches_cluster() -> None:
    # datum non-callable loop skips None (131) and sets on object (141)
    el = Element(tagName="DIV")
    sel = selection([[None, el]], [None])
    sel.datum(10)
    assert getattr(el, "__data__", None) == 10

    # filter string: n is None (156) and non-dom object (168)
    class Plain:
        pass

    out = selection([[None, Plain()]], [None]).filter("p")
    assert out.size() == 0

    # on(): dict branch in getter and unnamed listener (249/261) + not-list storage (251)
    dnode: dict = {"__on": [{"type": "x", "name": "", "listener": lambda *_a: 1}]}
    sdict = selection([[dnode]], [None])
    assert callable(sdict.on("x"))
    dnode["__on"] = {}  # type: ignore[assignment]
    assert sdict.on("x") is None

    # dispatch: fn() fallback (360-361) + ons not list (395)
    called = {"n": 0}

    def l0():  # noqa: ANN001
        called["n"] += 1

    el2 = Element(tagName="DIV")
    el2.__dict__["__on"] = [{"type": "t", "name": "", "listener": l0}]
    selection([[el2]], [None]).dispatch("t")
    assert called["n"] == 1
    el2.__dict__["__on"] = {}  # type: ignore[assignment]
    selection([[el2]], [None]).dispatch("t")

    # property getter: n None (503) and missing non-checked key (511)
    assert selection([[None]], [None]).property("x") is None
    assert selection([[Plain()]], [None]).property("x") is None

    # text/html getter: n None (539/567)
    assert selection([[None]], [None]).text() is None
    assert selection([[None]], [None]).html() is None

    # text/html non-callable setter skips None in group (559/570)
    a = Element(tagName="DIV")
    b = Element(tagName="DIV")
    selection([[a, None, b]], [None]).text("z")
    selection([[a, None, b]], [None]).html("<i></i>")


def test_style_get_computed_and_set_branches() -> None:
    # computed style branches (680, 685-687)
    class CS:
        def getPropertyValue(self, _k):  # noqa: ANN001
            return "computed"

    class DV:
        def __init__(self, cs):  # noqa: ANN001
            self._cs = cs

        def getComputedStyle(self, _n):  # noqa: ANN001
            return self._cs

    doc = {"defaultView": DV(CS())}
    node = {"style": {"getPropertyValue": lambda _k: ""}, "ownerDocument": doc}
    sel = selection([[node]], [None])
    assert sel.style("color") == "computed"

    # cs is dict with callable getPropertyValue (681-684)
    doc2 = {
        "defaultView": {
            "getComputedStyle": lambda _n: {"getPropertyValue": lambda _k: "c2"}
        }
    }
    node2 = {"style": {"getPropertyValue": lambda _k: ""}, "ownerDocument": doc2}
    assert selection([[node2]], [None]).style("color") == "c2"

    # cs has neither => return "" (685)
    doc3 = {"defaultView": {"getComputedStyle": lambda _n: {}}}
    node3 = {"style": {"getPropertyValue": lambda _k: ""}, "ownerDocument": doc3}
    assert selection([[node3]], [None]).style("color") == ""

    # set_one: style_obj None early return (694)
    selection([[{"ownerDocument": {}}]], [None]).style("color", "red")

    # set_one: dict removeProperty and setProperty branches (698-701, 707-710)
    seen: dict[str, str] = {}

    def setp(k, v, p=""):  # noqa: ANN001
        seen[k] = v

    def remp(k):  # noqa: ANN001
        seen.pop(k, None)

    style_obj = {
        "setProperty": setp,
        "removeProperty": remp,
        "getPropertyValue": lambda _k: "",
    }
    node4 = {"style": style_obj}
    s4 = selection([[node4, None]], [None])
    s4.style("color", "red")
    s4.style("color", None)

    # inline empty + no defaultView => falls through and returns inline "" (684)
    node5 = {"style": {"getPropertyValue": lambda _k: ""}, "ownerDocument": {}}
    assert selection([[node5]], [None]).style("color") == ""


def test_remaining_small_branches_order_classed_style_remove_children_attr() -> None:
    # order: skip None inside reversed loop (210)
    p = Element(tagName="DIV")
    a = Element(tagName="A")
    b = Element(tagName="B")
    p.appendChild(a)
    p.appendChild(b)
    selection([[a, None, b]], [p]).order()

    # property non-callable setter skips None (531)
    selection([[a, None]], [None]).property("x", 1)

    # html getter non-dict path (570)
    assert selection([[a]], [None]).html() == a.innerHTML

    # classed getter when node None (596)
    assert selection([[None]], [None]).classed("x") is False

    # classed callable setter skips None (618-622) and else setter skips None (629)
    def cv(this, d, i, nodes):  # noqa: ANN001
        return True

    selection([[a, None]], [None]).classed("x", cv)
    selection([[a, None]], [None]).classed("x", True)

    # style getter when node None (638) and style_obj missing => None (687)
    assert selection([[None]], [None]).style("color") is None
    assert selection([[{"ownerDocument": {}}]], [None]).style("color") is None

    # style callable setter loop skips None (715-719) and non-callable skips None (726)
    def sv(this, d, i, nodes):  # noqa: ANN001
        return "red"

    selection([[{"style": {"setProperty": lambda *_a: None}}, None]], [None]).style(
        "color", sv
    )
    selection([[{"style": {"setProperty": lambda *_a: None}}, None]], [None]).style(
        "color", "red"
    )

    # remove: ValueError branch (942-944)
    class Parent:
        def removeChild(self, _child):  # noqa: ANN001
            raise ValueError("nope")

    parent = Parent()
    child = Element(tagName="C")
    child.parentNode = parent  # type: ignore[assignment]
    selection([[child]], [None]).remove()

    # selectChildren: skip None node (956)
    assert selection([[None]], [None]).selectChildren().size() == 0

    # selectChild: default match None -> "*" (971) + callable matcher returns None (981)
    host = Element(tagName="DIV")
    host.appendChild(Element(tagName="X"))
    assert selection([[host]], [None]).selectChild().node() is not None

    def pick_none(this, d, i, nodes):  # noqa: ANN001
        return False

    assert selection([[host]], [None]).selectChild(pick_none).node() is None

    # selectChild: string path return None (991)
    assert selection([[host]], [None]).selectChild("nope").node() is None

    # attr getter when node None (1079)
    assert selection([[None]], [None]).attr("x") is None


def test_enter_append_and_insert_more_missing_branches() -> None:
    parent = Element(tagName="DIV")

    # enter append where create returns None (786-787)
    en = EnterNode(parent, 1)
    ent_sel = selection([[en]], [parent])

    def make_none(_this, *_a):  # noqa: ANN001
        return None

    assert ent_sel.append(make_none).node() is None

    # enter append where parent has appendChild but no insertBefore (790-791)
    class P:
        def __init__(self) -> None:
            self.children: list[Any] = []

        def appendChild(self, child):  # noqa: ANN001
            self.children.append(child)

    p = P()
    en2 = EnterNode(p, 2)

    def make_child(_p):  # noqa: ANN001
        return Element(tagName="X")

    selection([[en2]], [p]).append(lambda *_a: make_child(p))
    assert len(p.children) == 1

    # non-enter append: callable create returns None (820-821)
    host = Element(tagName="DIV")
    out = selection([[host]], [None]).append(lambda *_a: None)
    assert out.node() is None

    # enter insert before callable path (839-842) and en None (863-864)
    en3 = EnterNode(parent, 3)

    def before_fn(this, d, i, nodes):  # noqa: ANN001
        return None

    selection([[en3, None]], [parent]).insert("p", before_fn)

    # enter insert: parent has appendChild but no insertBefore (874-875)
    en4 = EnterNode(p, 4)
    selection([[en4]], [p]).insert("p", None)
    assert len(p.children) >= 2


def test_insert_non_enter_missing_branches() -> None:
    host = Element(tagName="DIV")
    sel = selection([[host]], [None])

    # child None (920-921)
    out = sel.insert(lambda *_a: None, "x")
    assert out.node() is None

    # appendChild branch when no insertBefore (925-926)
    class H:
        def __init__(self) -> None:
            self.children: list[Any] = []

        def appendChild(self, child):  # noqa: ANN001
            self.children.append(child)

        def querySelector(self, _s):  # noqa: ANN001
            return None

    h = H()
    selection([[h]], [None]).insert(lambda *_a: Element(tagName="Y"), "nope")
    assert len(h.children) == 1


def test_attr_namespaced_dict_branches_set_and_remove() -> None:
    store: dict[tuple[str, str], str] = {}

    def get_ns(uri, local):  # noqa: ANN001
        return store.get((uri, local))

    def set_ns(uri, local, v):  # noqa: ANN001
        store[(uri, local)] = v

    def rem_ns(uri, local):  # noqa: ANN001
        store.pop((uri, local), None)

    dnode = {
        "getAttributeNS": get_ns,
        "setAttributeNS": set_ns,
        "removeAttributeNS": rem_ns,
    }
    sel = selection([[dnode]], [None])
    sel.attr("xlink:href", "a")
    assert sel.attr("xlink:href") == "a"
    sel.attr("xlink:href", None)
    assert sel.attr("xlink:href") is None


def test_attr_get_set_remove_for_dict_and_namespaced_object() -> None:
    # dict-based node branches
    store: dict[str, str] = {}

    def get_attr(name):  # noqa: ANN001
        return store.get(name)

    def set_attr(name, value):  # noqa: ANN001
        store[name] = value

    def rem_attr(name):  # noqa: ANN001
        store.pop(name, None)

    dnode = {
        "getAttribute": get_attr,
        "setAttribute": set_attr,
        "removeAttribute": rem_attr,
    }
    sel = selection([[dnode]], [None])
    sel.attr("x", "1")
    assert sel.attr("x") == "1"
    sel.attr("x", None)
    assert sel.attr("x") is None

    # namespaced Element branches (set/remove/getAttributeNS)
    el = Element(tagName="DIV")
    sel2 = selection([[el]], [None])
    sel2.attr("xlink:href", "a")
    assert sel2.attr("xlink:href") == "a"
    sel2.attr("xlink:href", None)
    assert sel2.attr("xlink:href") is None
