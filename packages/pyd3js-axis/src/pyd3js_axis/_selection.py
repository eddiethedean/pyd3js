"""Minimal d3-selection used by d3-axis (synchronous `transition()` for axis parity)."""

from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from typing import TYPE_CHECKING, Any, Protocol, cast

if TYPE_CHECKING:
    from ._transition import Transition

from ._data_join import bind_index, bind_key, connect_enter_next
from ._enter import EnterNode
from ._svg import Element

__all__ = ("Selection", "select_node", "create", "_as_element", "_datum_of")

Node = Any


class _DataCallable(Protocol):
    """Callback shape used by `selection.data(fn)` (parent, datum, index, parents)."""

    def __call__(
        self,
        parent: Element | None,
        datum: object,
        group_index: int,
        parents: list[Element | None],
    ) -> object: ...


def _datum_of(n: object) -> object:
    if isinstance(n, (Element, EnterNode)):
        return n.__data__
    return getattr(n, "__data__", None)


def _as_element(n: object) -> Element | None:
    return n if isinstance(n, Element) else None


def _arraylike(value: object) -> list[object]:
    if isinstance(value, (str, bytes, bytearray, memoryview)):
        return [value]
    if isinstance(value, Sequence) and not isinstance(
        value, (str, bytes, bytearray, memoryview)
    ):
        return list(cast(Sequence[object], value))
    return list(cast(Iterable[object], value))


def _creator(tag: str) -> Callable[[], Element]:
    def c() -> Element:
        return Element(tag)

    return c


def create(tag: str) -> "Selection":
    return Selection([[Element(tag)]], [None])


def select_node(node: Element) -> "Selection":
    return Selection([[node]], [node.parent if node.parent is not None else None])


class Selection:
    def __init__(
        self,
        groups: list[list[Node | None]],
        parents: list[Element | None],
    ) -> None:
        self._groups = groups
        self._parents = parents
        self._enter: list[list[EnterNode | None]] | None = None
        self._exit: list[list[Node | None]] | None = None

    def node(self) -> object | None:
        for g in self._groups:
            for n in g:
                if n is not None and not isinstance(n, EnterNode):
                    return n
        for g in self._groups:
            for n in g:
                if n is not None:
                    return n
        return None

    def selection(self) -> "Selection":
        return self

    def transition(
        self, context: object | None = None
    ) -> Transition:  # noqa: ANN401, ANN003
        from ._transition import Transition as _Tr, _wrap

        if context is None:
            return _wrap(self)
        if isinstance(context, _Tr):
            return _wrap(self, owner=context)
        return _wrap(self, owner=None)

    def call(self, f: Callable[..., object], *args: object) -> "Selection":
        f(self, *args)  # type: ignore[operator, misc, call-arg]
        return self

    def each(self, fn: Callable[..., object]) -> "Selection":
        for g in self._groups:
            for i, n in enumerate(g):
                if n is None:
                    continue
                fn(n, _datum_of(n), i, g)
        return self

    def select(
        self,
        sel: str | Callable[[object, object, int, list[object | None]], object | None],
    ) -> "Selection":
        subgroups: list[list[object | None]] = []
        for group in self._groups:
            sub: list[object | None] = []
            for i, node in enumerate(group):
                if node is None:
                    sub.append(None)
                    continue
                d = _datum_of(node)
                if isinstance(sel, str):
                    if isinstance(node, EnterNode):
                        sn = node.querySelector(sel)
                    else:
                        el = _as_element(node)
                        sn = el.query_selector(sel) if el else None
                else:
                    sn = sel(node, d, i, group)
                if sn is not None and isinstance(node, Element):
                    od = getattr(node, "__data__", None)
                    if od is not None and isinstance(sn, Element):
                        sn.__data__ = od
                sub.append(sn)
            subgroups.append(sub)
        return Selection(subgroups, self._parents)

    def selectAll(self, sel: str) -> "Selection":
        subgroups: list[list[Element | None]] = []
        new_parents: list[Element | None] = []
        for g in self._groups:
            for n in g:
                if n is None or isinstance(n, EnterNode):
                    continue
                el = _as_element(n)
                if el is None:
                    continue
                subgroups.append(
                    cast(list[Element | None], list(el.query_selector_all(sel)))
                )
                new_parents.append(el)
        return Selection(subgroups, new_parents)

    def data(
        self,
        value: object | Callable[..., object],
        key: Callable[..., object] | None = None,
    ) -> "Selection":
        parents = self._parents
        groups = self._groups
        m = len(groups)
        update: list[list[Node | None]] = [[] for _ in range(m)]
        enter: list[list[EnterNode | None]] = [[] for _ in range(m)]
        ex: list[list[Node | None]] = [[] for _ in range(m)]
        for j in range(m):
            parent = parents[j]
            group = list(groups[j])
            if callable(value):
                pdata = cast(_DataCallable, value)(
                    parent,
                    getattr(parent, "__data__", None) if parent is not None else None,
                    j,
                    parents,
                )
                data = _arraylike(pdata)
            else:
                data = _arraylike(value)
            if key is not None:
                u, en, x = bind_key(parent, cast(list, group), data, key)
            else:
                u, en, x = bind_index(parent, cast(list, group), data)
            connect_enter_next(en, u)
            update[j] = u
            enter[j] = en
            ex[j] = x
        out = Selection(update, parents)
        out._enter = enter
        out._exit = ex
        return out

    def enter(self) -> "Selection":
        if self._enter is None:
            return Selection([[] for _ in self._groups], self._parents)
        return Selection(self._enter, self._parents)

    def exit(self) -> "Selection":
        if self._exit is None:
            return Selection([[] for _ in self._groups], self._parents)
        return Selection(self._exit, self._parents)

    def append(self, name: str | Callable[[], Element]) -> "Selection":
        create_ = _creator(name) if isinstance(name, str) else name

        def one(n: object, _d: object, _i: int, _g: list[object | None]) -> Element:
            c = create_()
            if isinstance(n, EnterNode):
                out = n.appendChild(c)
                out.__data__ = n.__data__
                return out
            el = _as_element(n)
            if el is None:
                raise TypeError("append needs Element or EnterNode")
            return el.append_child(c)

        return self.select(one)

    def insert(self, name: str, before: str | None) -> "Selection":
        create_ = _creator(name)

        def one(n: object, _d: object, _i: int, _g: list[object | None]) -> Element:
            c = create_()
            ref = None
            if before:
                if isinstance(n, EnterNode):
                    ref = n.querySelector(before)
                else:
                    el = _as_element(n)
                    ref = el.query_selector(before) if el else None
            if isinstance(n, EnterNode):
                out = n.insertBefore(c, ref)
                out.__data__ = n.__data__
                return out
            el2 = _as_element(n)
            if el2 is None:
                raise TypeError("insert needs Element or EnterNode")
            return el2.insert_before(c, ref)

        return self.select(one)

    def attr(self, name: str, value: object | None = None) -> str | "Selection":
        if value is None:
            n0 = self.node()
            if isinstance(n0, Element):
                return n0.get_attribute(name) or ""
            return ""

        def apply_attr(n: object, d: object, i: int, g: list[object | None]) -> None:
            el = _as_element(n)
            if el is None:
                return
            if callable(value):
                v = cast(Callable[..., object], value)(n, d, i, g)
                if v is None:
                    el.remove_attribute(name)
                else:
                    el.set_attribute(name, str(v))
            else:
                el.set_attribute(name, str(value))

        return self.each(apply_attr)

    def text(self, value: object | None = None) -> str | "Selection":
        if value is None:
            n0 = self.node()
            if isinstance(n0, Element):
                return n0.text_content
            return ""

        def apply_text(n: object, d: object, i: int, g: list[object | None]) -> None:
            el = _as_element(n)
            if el is None:
                return
            if callable(value):
                v = cast(Callable[..., object], value)(n, d, i, g)
                el.text_content = "" if v is None else str(v)
            else:
                el.text_content = "" if value is None else str(value)

        return self.each(apply_text)

    def merge(self, other: "Selection") -> "Selection":
        merges: list[list[Node | None]] = []
        g0s = self._groups
        g1s = other._groups
        m = min(len(g0s), len(g1s))
        for j in range(m):
            a = g0s[j]
            b = g1s[j]
            n = len(a)
            mg: list[Node | None] = [None] * n
            for i in range(n):
                na = a[i] if i < len(a) else None
                nb = b[i] if i < len(b) else None
                mg[i] = na or nb
            merges.append(mg)
        for j in range(m, len(g0s)):
            merges.append(g0s[j])
        return Selection(merges, self._parents)

    def order(self) -> "Selection":
        for j, group in enumerate(self._groups):
            p = (
                _as_element(self._parents[j])
                if j < len(self._parents) and self._parents[j] is not None
                else None
            )
            if p is None:
                continue
            g = list(group)
            if not g:
                continue
            m_ = len(g) - 1
            nxt: object | None = g[m_] if m_ >= 0 else None
            for k in range(m_ - 1, -1, -1):
                node = g[k] if k < len(g) else None
                if (
                    nxt
                    and node
                    and not isinstance(nxt, EnterNode)
                    and not isinstance(node, EnterNode)
                ):
                    el = cast(Element, node)
                    nx = cast(Element, nxt)
                    try:
                        i_el = p.children.index(el)
                        i_nx = p.children.index(nx)
                    except ValueError:
                        nxt = el
                        continue
                    if i_el > i_nx:
                        p.insert_before(el, nx)
                nxt = node
        return self

    def filter(
        self,
        match: Callable[[object, object, int, list[object | None]], bool],
    ) -> "Selection":
        subgroups: list[list[Node | None]] = []
        for g in self._groups:
            sub: list[Node | None] = []
            for i, node in enumerate(g):
                if node is None:
                    sub.append(None)
                    continue
                if match(node, _datum_of(node), i, g):
                    sub.append(node)
            subgroups.append(sub)
        return Selection(subgroups, self._parents)

    def remove(self) -> "Selection":
        for g in self._groups:
            for n in g:
                if n is None or isinstance(n, EnterNode):
                    continue
                el = _as_element(n)
                if el is None:
                    continue
                par = el.parent
                if par is not None:
                    par.remove_child(el)
        return self
