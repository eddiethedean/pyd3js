from __future__ import annotations

from typing import Any, Iterator

from pyd3js_selection.selection.index import selection as _Selection


_id = 0


def new_id() -> int:
    global _id
    _id += 1
    return _id


class Transition:
    def __init__(self, groups: list[list[Any]], parents: list[Any], name: str | None, id: int) -> None:
        self._groups = groups
        self._parents = parents
        self._name = name
        self._id = id

    # Selection-like helpers (delegate to Selection methods via a temporary wrapper).
    def selection(self):
        from pyd3js_transition.transition.selection import transition_selection

        return transition_selection(self)

    def node(self):
        return _Selection(self._groups, self._parents).node()

    def nodes(self) -> list[Any]:
        return _Selection(self._groups, self._parents).nodes()

    def size(self) -> int:
        return _Selection(self._groups, self._parents).size()

    def empty(self) -> bool:
        return _Selection(self._groups, self._parents).empty()

    def each(self, fn):  # noqa: ANN001
        # Transition methods are chainable; unlike Selection.each, return self.
        def _call_value(f, this: Any, d: Any, i: int, nodes: list[Any]):  # noqa: ANN001
            try:
                return f(this, d, i, nodes)
            except TypeError:
                try:
                    return f(d, i, nodes)
                except TypeError:
                    try:
                        return f(d, i)
                    except TypeError:
                        try:
                            return f(this)
                        except TypeError:
                            try:
                                return f(d)
                            except TypeError:
                                return f()

        for group in self._groups:
            for i, node in enumerate(group):
                if node is None:
                    continue
                _call_value(fn, node, getattr(node, "__data__", None), i, group)
        return self

    def call(self, fn, *args):  # noqa: ANN001
        fn(self, *args)
        return self

    def __iter__(self) -> Iterator[Any]:
        return iter(self.nodes())

    # Methods borrowed from d3-selection's selection prototype.
    # These implementations use `self.select` / `self.selectAll`, so they work for
    # transitions as well (matching d3-transition's prototype wiring).
    def selectChild(self, match: Any = None):  # noqa: ANN001, N802
        # Port of d3-selection's selectChild, but returning Transition via `self.select`.
        if match is None:
            match = "*"

        if callable(match):
            fn = match

            def _pick(n, _d, _i, _nodes):  # noqa: ANN001
                for c in getattr(n, "childNodes", []):
                    try:
                        ok = fn(c, getattr(c, "__data__", None), 0, [c])
                    except TypeError:
                        ok = fn(c)
                    if ok:
                        return c
                return None

        else:
            sel = str(match)

            def _pick(n, _d, _i, _nodes):  # noqa: ANN001
                for c in getattr(n, "childNodes", []):
                    if hasattr(c, "querySelectorAll"):
                        if sel == "*" or c in c.parentNode.querySelectorAll(sel):
                            return c
                return None

        return self.select(_pick)

    def selectChildren(self, match: Any = None):  # noqa: ANN001, N802
        # Port of d3-selection's selectChildren; returns a Selection.
        if match is None:
            match = "*"
        sel = str(match)
        subgroups: list[list[Any]] = []
        parents: list[Any] = []
        for group in self._groups:
            for n in group:
                if n is None:
                    continue
                kids = list(getattr(n, "childNodes", []))
                if sel != "*":
                    kids = [
                        c
                        for c in kids
                        if hasattr(c, "querySelectorAll")
                        and c in c.parentNode.querySelectorAll(sel)
                    ]
                subgroups.append(kids)
                parents.append(n)
        return _Selection(subgroups, parents)

    # --- d3-transition API methods (ported) ---------------------------------
    def on(self, name: Any, listener: Any = ...):  # noqa: ANN001
        from pyd3js_transition.transition.on import on

        return on(self, name, listener)

    def tween(self, name: Any, value: Any = ...):  # noqa: ANN001
        from pyd3js_transition.transition.tween import tween

        if value is ...:
            return tween(self, name)
        return tween(self, name, value)

    def delay(self, value: Any = ...):  # noqa: ANN001
        from pyd3js_transition.transition.delay import delay

        return delay(self, value)

    def duration(self, value: Any = ...):  # noqa: ANN001
        from pyd3js_transition.transition.duration import duration

        return duration(self, value)

    def ease(self, value: Any = ...):  # noqa: ANN001
        from pyd3js_transition.transition.ease import ease

        return ease(self, value)

    def easeVarying(self, value: Any):  # noqa: ANN001
        from pyd3js_transition.transition.easeVarying import easeVarying

        return easeVarying(self, value)

    def transition(self) -> "Transition":
        from pyd3js_transition.transition.transition import transition_transition

        return transition_transition(self)

    def merge(self, other: Any) -> "Transition":  # noqa: ANN001
        from pyd3js_transition.transition.merge import merge

        return merge(self, other)

    def filter(self, match: Any) -> "Transition":  # noqa: ANN001
        from pyd3js_transition.transition.filter import filter as _filter

        return _filter(self, match)

    def select(self, select: Any) -> "Transition":  # noqa: ANN001
        from pyd3js_transition.transition.select import select as _select

        return _select(self, select)

    def selectAll(self, select: Any) -> "Transition":  # noqa: ANN001, N802
        from pyd3js_transition.transition.selectAll import selectAll as _selectAll

        return _selectAll(self, select)

    def attrTween(self, name: Any, value: Any = ...):  # noqa: ANN001, N802
        from pyd3js_transition.transition.attrTween import attrTween

        return attrTween(self, name, value)

    def styleTween(self, name: Any, value: Any = ..., priority: Any = ""):  # noqa: ANN001, N802
        from pyd3js_transition.transition.styleTween import styleTween

        return styleTween(self, name, value, priority)

    def textTween(self, value: Any = ...):  # noqa: ANN001, N802
        from pyd3js_transition.transition.textTween import textTween

        return textTween(self, value)

    def attr(self, name: Any, value: Any = None):  # noqa: ANN001
        from pyd3js_transition.transition.attr import attr

        return attr(self, name, value)

    def style(self, name: Any, value: Any = None, priority: Any = ""):  # noqa: ANN001
        from pyd3js_transition.transition.style import style

        return style(self, name, value, priority)

    def text(self, value: Any = None):  # noqa: ANN001
        from pyd3js_transition.transition.text import text

        return text(self, value)

    def remove(self):  # noqa: ANN001
        from pyd3js_transition.transition.remove import remove

        return remove(self)

    def end(self):  # noqa: ANN001
        from pyd3js_transition.transition.end import end

        return end(self)


def transition(name: Any = None) -> "Transition":
    # d3: export default function transition(name) { return selection().transition(name); }
    from pyd3js_transition.selection.transition import selection_transition

    return selection_transition(_Selection(), name)

