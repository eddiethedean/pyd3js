"""Targeted tests for remaining branches (100% line coverage)."""

from __future__ import annotations

import pytest

from pyd3js_axis import axisLeft
from pyd3js_axis._axis import Axis
from pyd3js_axis._data_join import bind_index, bind_key, connect_enter_next
from pyd3js_axis._enter import EnterNode
from pyd3js_axis._identity import identity
from pyd3js_axis._selection import (
    Selection,
    _arraylike,
    _datum_of,
    create,
    select_node,
)
from pyd3js_axis._svg import Element, outer_html
from pyd3js_axis._transition import Transition, _wrap


def test_datum_of_generic_node() -> None:
    class N:
        __data__ = 42

    assert _datum_of(N()) == 42


def test_arraylike_generic_iterable() -> None:
    def gen():
        yield 1
        yield 2

    assert _arraylike(gen()) == [1, 2]


def test_axis_type_error_bad_selection() -> None:
    from .test_transition_branch import MockLinear

    class Bad:
        def selection(self):
            return "not-a-selection"

    s = MockLinear()
    a = axisLeft(s).tickValues([0.0, 1.0])
    with pytest.raises(TypeError, match="Selection"):
        a(Bad())


def test_axis_scale_without_ticks_uses_domain() -> None:
    class S:
        def __init__(self) -> None:
            self._d = [0.0, 1.0]

        def __call__(self, d: object) -> float:
            return float(d)

        def domain(self):
            return list(self._d)

        def range(self):
            return [0.0, 1.0]

        def copy(self):
            return self

    root = create("svg").node()
    g = Element("g")
    assert root is not None
    root.append_child(g)
    axisLeft(S())(select_node(g))
    assert "path" in outer_html(g)


def test_center_band_round() -> None:
    class Band:
        def __init__(self) -> None:
            self._d = ["a", "b"]

        def __call__(self, d: object) -> float:
            return float(["a", "b"].index(str(d)))

        def bandwidth(self) -> float:
            return 1.0

        def round(self) -> bool:
            return True

        def domain(self):
            return self._d

        def range(self):
            return [0.0, 2.0]

        def copy(self):
            return self

    root = create("svg").node()
    g = Element("g")
    assert root is not None
    root.append_child(g)
    axisLeft(Band())(select_node(g).transition())
    assert "tick" in outer_html(g)


def test_invoke_tick_format_none_and_non_callable() -> None:
    class S1:
        tickFormat = 1  # not callable → identity

    from pyd3js_axis._axis import _invoke_tick_format

    f = _invoke_tick_format(S1(), [])
    assert f(3) == identity(3)

    class S2:
        def tickFormat(self):
            return None

    f2 = _invoke_tick_format(S2(), [])
    assert f2(5) == 5  # tickFormat() returned None → identity

    class S3:
        def tickFormat(self):
            return str

    f3 = _invoke_tick_format(S3(), [])
    assert f3(5) == "5"


def test_axis_custom_tick_format() -> None:
    from .test_transition_branch import MockLinear

    s = MockLinear()
    root = create("svg").node()
    g = Element("g")
    assert root is not None
    root.append_child(g)
    a = axisLeft(s).tickFormat(lambda d, *_: f"#{d}")
    a.tickValues([1.0])
    a(select_node(g))
    assert "#1" in outer_html(g)


def test_axis_scale_setter_and_tick_setters() -> None:
    s1, s2 = object(), object()
    a: Axis = axisLeft(s1)
    assert a.scale(s2) is a
    assert a.scale() is s2
    assert a.tickSize(4) is a and a.tickSize() == 4.0
    assert a.tickSizeInner(3) is a and a.tickSizeInner() == 3.0
    assert a.tickSizeOuter(2) is a and a.tickSizeOuter() == 2.0
    assert a.tickPadding(1) is a and a.tickPadding() == 1.0
    assert a.offset(0.25) is a and a.offset() == 0.25


def test_enter_tfn_enter_node_and_bad_parent_callable() -> None:
    from .test_transition_branch import MockLinear

    s = MockLinear()
    root = create("svg").node()
    g = Element("g")
    assert root is not None
    root.append_child(g)
    ax = axisLeft(s).tickValues([0.0, 1.0])
    ax(select_node(g).transition())
    ax.tickValues([0.0, 0.5, 1.0])
    g.d3__axis = None
    g.__axis = lambda d: (_ for _ in ()).throw(ValueError("x"))  # noqa: B008
    ax(select_node(g).transition())
    assert 'class="tick"' in outer_html(g)


def test_bind_index_exit_and_enter() -> None:
    p = Element("g")
    a = Element("a")
    b = Element("b")
    p.append_child(a)
    p.append_child(b)
    a.__data__ = 0
    b.__data__ = 1
    u, e, x = bind_index(p, [a, b], [10, 20, 30])
    assert u[2] is None and e[2] is not None
    u2, e2, x2 = bind_index(p, [a, b, b], [1])
    assert x2[1] is b or x2[2] is b


def test_bind_key_duplicate_in_group() -> None:
    p = Element("g")
    n0 = Element("t")
    n1 = Element("t")
    n0.__data__ = 1
    n1.__data__ = 1
    p.append_child(n0)
    p.append_child(n1)

    def key(d: object) -> object:
        return d

    u, e, ex = bind_key(p, [n0, n1], [1, 2], key)
    assert ex[0] is n0 or ex[1] is n1


def test_connect_enter_next_wiring() -> None:
    p = Element("g")
    en0 = EnterNode(p, 0, None)
    en1 = EnterNode(p, 1, None)
    el = Element("x")
    connect_enter_next([en0, en1], [None, el])
    assert en0._next is el


def test_selection_node_variants() -> None:
    en = EnterNode(Element("g"), None, None)
    s = Selection([[en]], [None])
    assert s.node() is en
    s2 = Selection([[None]], [None])
    assert s2.node() is None


def test_selection_transition_with_context() -> None:
    g = Element("g")
    s = select_node(g)
    t0 = s.transition()
    t1 = s.transition(t0)
    assert isinstance(t1, Transition)


def test_selection_select_string_enter() -> None:
    p = Element("g")
    en = EnterNode(p, 1, None)
    s = Selection([[en]], [p])
    sub = s.select("line")
    assert sub._groups[0][0] is None


def test_selection_select_all_skips_enter() -> None:
    p = Element("g")
    en = EnterNode(p, 1, None)
    s = Selection([[en]], [p])
    sa = s.selectAll("line")
    assert sa._groups == []


def test_selection_data_callable() -> None:
    root = create("svg").node()
    p = Element("g")
    assert root is not None
    root.append_child(p)
    p.__data__ = 2
    s = select_node(p)
    s2 = s.data(lambda *args: [1, 2])
    assert s2._enter is not None


def test_selection_empty_enter_exit() -> None:
    s = create("svg")
    assert s.enter()._groups[0] == []
    assert s.exit()._groups[0] == []


def test_selection_append_type_error() -> None:
    s = Selection([[object()]], [None])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="append"):
        s.append("x")


def test_selection_insert_type_error() -> None:
    s = Selection([[object()]], [None])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="insert"):
        s.insert("g", None)


def test_selection_attr_text_getters() -> None:
    p = Element("e")
    p.set_attribute("k", "v")
    s = select_node(p)
    assert s.attr("k") == "v"
    p.text_content = "hi"
    assert s.text() == "hi"
    s2 = Selection([[None]], [None])
    assert s2.attr("a") == ""
    assert s2.text() == ""


def test_selection_attr_callable_remove() -> None:
    p = Element("e")
    p.set_attribute("a", "1")
    s = select_node(p)

    def _rem(_n, _d, _i, _g):
        return None

    s.attr("a", _rem)
    assert p.get_attribute("a") is None


def test_selection_text_callable_none() -> None:
    p = Element("e")
    s = select_node(p)

    def _n(_n, _d, _i, _g):
        return None

    s.text(_n)
    assert p.text_content == ""


def test_selection_merge_and_order() -> None:
    g = Element("g")
    a = Element("a")
    c = Element("c")
    b = Element("b")
    g.append_child(a)
    g.append_child(c)
    g.append_child(b)
    s1 = select_node(a)
    s2 = select_node(b)
    m = s1.merge(s2)
    assert m.node() is a
    s3 = select_node(g).selectAll("a")
    s3.order()


def test_selection_filter_remove() -> None:
    g = Element("g")
    a = Element("a")
    g.append_child(a)
    s = select_node(g)
    s2 = s.filter(lambda n, d, i, gr: False)
    assert s2._groups[0] == []
    s3 = select_node(a)
    s3.remove()
    assert a.parent is None


def test_selection_select_functional() -> None:
    g = Element("g")
    c = Element("c")
    g.append_child(c)
    s = select_node(g)
    s2 = s.select(lambda n, d, i, gr: c)
    assert s2.node() is c


def test_transition_exhaustive() -> None:
    r = create("svg").node()
    g = Element("g")
    assert r is not None
    r.append_child(g)
    s = select_node(g)
    t: Transition = _wrap(s)
    t.call(lambda tr, *a: None, 1)  # noqa: ARG005
    t2: Transition = t.data([1], key=None)
    t2.select("x")
    t2.selectAll("line")
    t2.append("g")
    t2.insert("path", None)
    t2.enter()
    t2.exit()
    t2.order()
    t2.filter(lambda *a: True)  # noqa: ARG005
    t2.merge(s)
    t3: Transition = t2.transition()
    t4: Transition = t2.transition(t3)
    t4.attr("x", "1")
    t4.text("a")
    t4.remove()
    g2 = Element("g")
    r.append_child(g2)
    s2 = select_node(g2)
    t5: Transition = s2.transition()
    assert t5.text() == ""
    t6: Transition = s2.transition()
    assert t6.attr("nope") == ""


def test_svg_element_edge_cases() -> None:
    e = Element("e")
    e.set_attribute("a", "1")
    e.set_attribute("a", "2")
    e.set_attribute("b", "1")
    e.set_attribute("a", None)  # removes all `a` name entries
    e.remove_attribute("b")
    assert e.get_attribute("a") is None
    assert e.get_attribute("b") is None
    e2 = Element("x")
    e2.append_child(e)
    e2.append_child(e)  # reparent
    e3 = Element("x")
    e2.insert_before(e, None)
    e2.insert_before(e, e3)  # before not in list → append
    m = Element("m")
    e2.insert_before(m, e)  # old parent edge
    e2.has_class("x")
    assert outer_html(e2) != ""


def test_svg_id_selector() -> None:
    root = Element("svg")
    e = Element("e")
    e.set_attribute("id", "i")
    root.append_child(e)
    assert e.query_selector("#i") is None
    assert root.query_selector("#i") is e
    e.set_attribute("class", "a b")
    assert e.has_class("a")
    assert root.query_selector_all(".a") == [e]


def test_invoke_ticks_uses_domain_when_no_ticks() -> None:
    class S:
        # Truthy, non-callable `ticks` → `domain()` branch in _invoke_ticks
        ticks: int = 1

        def __init__(self) -> None:
            pass

        def __call__(self, x: object) -> float:
            return float(x)

        def domain(self) -> list[float]:
            return [0.0, 1.0]

        def range(self) -> tuple[float, float]:
            return (0.0, 1.0)

        def copy(self) -> S:
            return self

    root = create("svg").node()
    g = Element("g")
    assert root is not None
    root.append_child(g)
    a = axisLeft(S())
    a(select_node(g).transition())
    assert "tick" in outer_html(g)


def test_data_join_rejects_non_element_parent() -> None:
    from pytest import raises

    with raises(TypeError, match="data join parent"):
        bind_index(None, [], [1])  # type: ignore[arg-type]



def test_bind_key_skip_enter_in_group() -> None:
    p = Element("g")
    u, e, ex = bind_key(
        p,
        [EnterNode(p, 1, None), Element("x")],  # type: ignore[list-item]
        [1, 2],
        lambda d: d,
    )
    assert e[0] is not None or u[0] is not None

def test_parent_element_type_error() -> None:
    from pytest import raises

    with raises(TypeError, match="data join parent"):
        bind_key(object(), [Element("x")], [1], lambda d: d)  # type: ignore[arg-type]


def test_enter_node_mutation_and_queries() -> None:
    p = Element("g")
    ch = Element("ch")
    en = EnterNode(p, 99, "k")
    assert en.parent is p
    e2 = en.querySelector("ch")
    assert e2 is None
    p.append_child(ch)
    e3 = en.querySelector("ch")
    assert e3 is ch
    en.querySelectorAll("ch")
    en.next_sibling = ch
    assert en.next_sibling is ch
    assert "EnterNode" in repr(en)


def test_svg_insert_before_reparenting_edge() -> None:
    a = Element("a")
    b1 = Element("b1")
    b2 = Element("b2")
    a.append_child(b1)
    a.append_child(b2)
    a.insert_before(b1, b2)


def test_transition_each_and_opaque_context() -> None:
    r = create("svg").node()
    g = Element("g")
    assert r is not None
    r.append_child(g)
    s = select_node(g)
    s.call(lambda *a: None)  # noqa: ARG005
    t0 = s.transition(3)  # type: ignore[arg-type]
    t = t0.each(lambda *a: None)  # noqa: ARG005
    t.transition(1)  # Transition.transition non-Transition context
    assert t is not None


def test_arraylike_string_is_single_group() -> None:
    p = Element("g")
    root = create("svg").node()
    assert root is not None
    root.append_child(p)
    s = select_node(p)
    s2 = s.data("a")
    assert s2._groups[0][0] is not None


def test_select_all_skips_non_element_node() -> None:
    p = Element("g")
    s = Selection([[object()]], [p])  # type: ignore[list-item]
    assert s.selectAll("x")._groups == []


def test_insert_with_before_selector() -> None:
    p = Element("g")
    t = Element("t")
    p.append_child(t)
    s = select_node(p)
    s.insert("a", "t")


def test_attr_on_enter_node_is_noop() -> None:
    p = Element("g")
    en = EnterNode(p, 1, None)
    s = Selection([[en]], [p])
    s.attr("a", "1")
    s.text("x")


def test_merge_longer_left() -> None:
    a, b, c = Element("a"), Element("b"), Element("c")
    s1 = Selection([[a, b], [c]], [None, None])
    s2 = Selection([[a]], [None])
    m = s1.merge(s2)
    assert len(m._groups) == 2


def test_order_with_none_parent() -> None:
    a = Element("a")
    s = Selection([[a]], [None])  # parent list None
    s.order()


def test_order_empty_group() -> None:
    s = Selection([[]], [Element("g")])
    s.order()


def test_order_value_error_index_stale_child() -> None:
    p = Element("g")
    a, b = Element("a"), Element("b")
    p.append_child(a)
    p.append_child(b)
    p.children = [b]  # a detached from list but `a` still in selection
    a.parent = p
    s = Selection([[a, b]], [p])
    s.order()


def test_order_insert_before_reorders() -> None:
    p = Element("g")
    a, b = Element("a"), Element("b")
    p.append_child(b)
    p.append_child(a)
    s = Selection([[a, b]], [p])  # desired order: a before b in DOM
    s.order()
    assert p.children[0] is a
    assert p.children[1] is b


def test_filter_with_none_in_group() -> None:
    s = Selection([[None, Element("a")]], [Element("g")])
    s2 = s.filter(lambda n, d, i, g: n is not None and isinstance(n, Element))
    assert s2._groups[0][1] is not None


def test_remove_skips_enter_node() -> None:
    p = Element("g")
    en = EnterNode(p, 1, None)
    s = Selection([[en]], [p])
    s.remove()
    s2 = Selection([[object()]], [p])  # type: ignore[list-item]
    s2.remove()  # non-Element, non-EnterNode: no-op


def test_invoke_ticks_empty_no_domain() -> None:
    class S:
        ticks: int = 1

        def __call__(self, x: object) -> float:
            return 0.0

        def range(self) -> tuple[float, float]:
            return (0.0, 1.0)

        def copy(self) -> S:
            return self

    root = create("svg").node()
    g = Element("g")
    assert root is not None
    root.append_child(g)
    a = axisLeft(S())
    a(select_node(g).transition())
    assert "path" in outer_html(g)


def test_data_join_parent_is_enter_node() -> None:
    p = Element("g")
    ch = Element("c")
    p.append_child(ch)
    ch.__data__ = 1
    u, e, ex = bind_key(EnterNode(p, 0, None), [ch], [1, 2], lambda d: d)
    assert u[0] is ch or e[0] is not None
