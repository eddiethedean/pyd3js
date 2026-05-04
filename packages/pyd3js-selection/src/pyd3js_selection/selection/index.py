from __future__ import annotations

from functools import cmp_to_key
from typing import Any, Iterator

import pyd3js_selection._globals as g
from pyd3js_selection.creator import creator
from pyd3js_selection.namespace import namespace as _namespace


root = [None]


class EnterNode:
    def __init__(self, parent: Any, data: Any):
        self._parent = parent
        self.__data__ = data
        self._next = None


def _call_value(fn, this: Any, d: Any, i: int, nodes: list[Any]):  # noqa: ANN001
    # D3 callbacks are typically (d, i, nodes) with `this` bound; our port
    # passes `this` explicitly for convenience.
    try:
        return fn(this, d, i, nodes)
    except TypeError:
        try:
            return fn(d, i, nodes)
        except TypeError:
            try:
                return fn(d, i)
            except TypeError:
                try:
                    return fn(this)
                except TypeError:
                    try:
                        return fn(d)
                    except TypeError:
                        return fn()


class selection:
    def __init__(
        self,
        groups: list[list[Any]] | None = None,
        parents: list[Any] | None = None,
        enter: Any = None,
        exit: Any = None,
    ) -> None:
        if groups is None and parents is None:
            doc = g.document
            if doc is None:
                self._groups = [[None]]
                self._parents = root
            else:
                self._groups = [[doc.documentElement]]
                self._parents = root
        else:
            self._groups = groups or [[]]
            self._parents = parents or root
        self._enter = enter
        self._exit = exit

    def selection(self) -> "Selection":
        return self

    def node(self):
        for g in self._groups:
            for n in g:
                if n is not None:
                    return n
        return None

    def nodes(self) -> list[Any]:
        out: list[Any] = []
        for g in self._groups:
            for n in g:
                if n is not None:
                    out.append(n)
        return out

    def size(self) -> int:
        return len(self.nodes())

    def empty(self) -> bool:
        return self.node() is None

    def each(self, fn):
        for group in self._groups:
            for i, n in enumerate(group):
                if n is None:
                    continue
                _call_value(fn, n, getattr(n, "__data__", None), i, group)
        return self

    def call(self, fn, *args):
        fn(self, *args)
        return self

    def datum(self, value: Any = ...):
        if value is ...:
            n = self.node()
            if n is None:
                return None
            if hasattr(n, "__dict__") and "__data__" in n.__dict__:
                return n.__dict__.get("__data__")
            if isinstance(n, dict):
                return n.get("__data__")
            return getattr(n, "__data__", None)

        if callable(value):
            for group in self._groups:
                for i, n in enumerate(group):
                    if n is None:
                        continue
                    v = _call_value(value, n, getattr(n, "__data__", None), i, group)
                    if v is None:
                        if isinstance(n, dict):
                            n.pop("__data__", None)
                        elif hasattr(n, "__dict__") and "__data__" in n.__dict__:
                            del n.__dict__["__data__"]
                    else:
                        if isinstance(n, dict):
                            n["__data__"] = v
                        else:
                            setattr(n, "__data__", v)
        else:
            for group in self._groups:
                for n in group:
                    if n is None:
                        continue
                    if value is None:
                        if isinstance(n, dict):
                            n.pop("__data__", None)
                        elif hasattr(n, "__dict__") and "__data__" in n.__dict__:
                            del n.__dict__["__data__"]
                    else:
                        if isinstance(n, dict):
                            n["__data__"] = value
                        else:
                            setattr(n, "__data__", value)
        return self

    def filter(self, match: Any) -> "selection":
        if callable(match):
            fn = match

            def _keep(n, d, i, nodes):  # noqa: ANN001
                return bool(_call_value(fn, n, d, i, nodes))

        else:
            sel = str(match)

            def _keep(n, _d, _i, _nodes):  # noqa: ANN001
                if n is None:
                    return False
                # Simple: reuse our DOM selector matching by querying from the node's root.
                if hasattr(n, "querySelectorAll"):
                    # `*` should match any element.
                    if sel == "*":
                        return True
                    # Comma unions are supported by our querySelectorAll.
                    return n in n.parentNode.querySelectorAll(sel) if getattr(n, "parentNode", None) else False
                return False

        subgroups: list[list[Any]] = []
        for group in self._groups:
            subgroup: list[Any] = []
            for i, n in enumerate(group):
                if n is None:
                    continue
                d = getattr(n, "__data__", None)
                if _keep(n, d, i, group):
                    subgroup.append(n)
            subgroups.append(subgroup)
        return selection(subgroups, self._parents)

    def merge(self, other: Any) -> "selection":
        # Supports merge(selection) and merge(transition-like {selection()})
        if hasattr(other, "selection") and callable(other.selection):
            other = other.selection()
        other_groups = getattr(other, "_groups", [])

        merged: list[list[Any]] = []
        for i, group in enumerate(self._groups):
            if i >= len(other_groups):
                merged.append(group)  # reuse
                continue
            og = other_groups[i]
            m = max(len(group), len(og))
            out: list[Any] = [None] * m
            for j in range(m):
                a = group[j] if j < len(group) else None
                b = og[j] if j < len(og) else None
                out[j] = a if a is not None else b
            merged.append(out)
        return selection(merged, self._parents)

    def order(self) -> "selection":
        # Reorder DOM elements to match current group order.
        for group in self._groups:
            # find next node to insert before while walking backwards
            next_node = None
            for n in reversed(group):
                if n is None:
                    continue
                parent = getattr(n, "parentNode", None)
                if parent is not None and hasattr(parent, "insertBefore"):
                    parent.insertBefore(n, next_node)
                next_node = n
        return self

    def sort(self, compare: Any = None) -> "selection":
        if compare is None:
            def compare(a, b):  # noqa: ANN001
                return (a > b) - (a < b)

        def cmp_nodes(a, b):  # noqa: ANN001
            return int(compare(getattr(a, "__data__", None), getattr(b, "__data__", None)))

        subgroups: list[list[Any]] = []
        for group in self._groups:
            nodes = [n for n in group if n is not None]
            missing = len(group) - len(nodes)
            nodes_sorted = sorted(nodes, key=cmp_to_key(cmp_nodes))
            subgroups.append(nodes_sorted + [None] * missing)

        out = selection(subgroups, self._parents)
        return out.order()

    def on(self, typename: Any, listener: Any = ..., capture: Any = False):
        s = str(typename)
        parts = s.split(".")
        typ = parts[0] if parts and parts[0] else ""
        name = parts[1] if len(parts) > 1 else ""

        def _get_one(n):  # noqa: ANN001
            ons = None
            if hasattr(n, "__dict__"):
                ons = n.__dict__.get("__on")
            if isinstance(n, dict):
                ons = n.get("__on")
            if not isinstance(ons, list):
                return None
            for o in ons:
                if o.get("type") != typ:
                    continue
                if name:
                    if o.get("name") == name:
                        return o.get("listener")
                else:
                    # If no name is specified, return only unnamed listener.
                    if not o.get("name"):
                        return o.get("listener")
            return None

        if listener is ...:
            # getter
            n = self.node()
            if n is None:
                return None
            return _get_one(n)

        # setter / remover
        if typ == "" and listener is not None:
            # on(".name", fn) is no-op
            return self

        for group in self._groups:
            for n in group:
                if n is None:
                    continue
                if hasattr(n, "__dict__"):
                    ons = n.__dict__.setdefault("__on", [])
                elif isinstance(n, dict):
                    ons = n.setdefault("__on", [])
                else:
                    try:
                        ons = getattr(n, "__on")
                    except Exception:  # noqa: BLE001
                        ons = []
                        setattr(n, "__on", ons)

                if listener is None:
                    # remove
                    if name and typ:
                        ons[:] = [o for o in ons if not (o.get("type") == typ and o.get("name") == name)]
                    elif name and not typ:
                        ons[:] = [o for o in ons if o.get("name") != name]
                    elif typ and not name:
                        ons[:] = [o for o in ons if not (o.get("type") == typ and not o.get("name"))]
                    # try to remove via DOM API
                    if hasattr(n, "removeEventListener") and typ:
                        try:
                            n.removeEventListener(typ, listener, bool(capture))  # type: ignore[arg-type]
                        except Exception:  # noqa: BLE001
                            pass
                    continue

                # add / replace
                # remove existing same type+name
                ons[:] = [o for o in ons if not (o.get("type") == typ and o.get("name") == name)]
                ons.append({"type": typ, "name": name, "listener": listener, "capture": bool(capture)})
                if typ:
                    if isinstance(n, dict) and callable(n.get("addEventListener")):
                        n["addEventListener"](typ, listener, bool(capture))
                    elif hasattr(n, "addEventListener"):
                        n.addEventListener(typ, listener, bool(capture))  # type: ignore[arg-type]
        return self

    def dispatch(self, typ: Any, params: Any = None):
        class Event:  # minimal CustomEvent-like
            def __init__(self, type_: str, bubbles: bool = False, cancelable: bool = False, detail: Any = None) -> None:
                self.type = type_
                self.bubbles = bubbles
                self.cancelable = cancelable
                self.detail = detail

        def _call_listener(fn, this, e, d):  # noqa: ANN001
            try:
                return fn(this, e, d)
            except TypeError:
                try:
                    return fn(e, d)
                except TypeError:
                    return fn(e, d)
                try:
                    return fn(e)
                except TypeError:
                    return fn()

        for group in self._groups:
            for i, n in enumerate(group):
                if n is None:
                    continue
                d = getattr(n, "__data__", None)
                if isinstance(n, dict):
                    d = n.get("__data__")

                p = params
                if callable(params):
                    p = _call_value(params, n, d, i, group)
                bubbles = bool(p.get("bubbles")) if isinstance(p, dict) and "bubbles" in p else False
                cancelable = bool(p.get("cancelable")) if isinstance(p, dict) and "cancelable" in p else False
                detail = p.get("detail") if isinstance(p, dict) else None
                e = Event(str(typ), bubbles=bubbles, cancelable=cancelable, detail=detail)

                ons = None
                if hasattr(n, "__dict__"):
                    ons = n.__dict__.get("__on")
                if isinstance(n, dict):
                    ons = n.get("__on")
                if not isinstance(ons, list):
                    ons = []
                for o in ons:
                    if o.get("type") == str(typ):
                        _call_listener(o.get("listener"), n, e, d)
        return self

    def data(self, value: Any = ..., key: Any = None):
        if value is ...:
            return [getattr(n, "__data__", None) for n in self.nodes()]
        if value is None:
            raise TypeError("null data")

        enter_groups: list[list[Any]] = []
        exit_groups: list[list[Any]] = []

        new_groups: list[list[Any]] = []
        new_parents: list[Any] = []

        for parent_index, (group, parent) in enumerate(zip(self._groups, self._parents, strict=False)):
            if callable(value):
                parent_data = getattr(parent, "__data__", None) if parent is not None else None
                data_list = list(_call_value(value, parent, parent_data, parent_index, self._parents))  # type: ignore[misc]
            else:
                data_list = list(value)

            m = len(data_list)
            update: list[Any] = [None] * m
            enter: list[Any] = [None] * m
            exit_: list[Any] = [None] * len(group)

            if key is None:
                for i in range(m):
                    d = data_list[i]
                    if i < len(group) and group[i] is not None:
                        node = group[i]
                        setattr(node, "__data__", d)
                        update[i] = node
                    else:
                        enter[i] = EnterNode(parent, d)
                for j in range(m, len(group)):
                    exit_[j] = group[j]
            else:
                # Keyed join.
                node_by_key: dict[str, Any] = {}
                for j, node in enumerate(group):
                    if node is None:
                        continue
                    k = str(_call_value(key, node, getattr(node, "__data__", None), j, group))
                    if k in node_by_key:
                        exit_[j] = node
                    else:
                        node_by_key[k] = node

                for i, d in enumerate(data_list):
                    k = str(_call_value(key, parent, d, i, data_list))
                    if k in node_by_key:
                        node = node_by_key.pop(k)
                        setattr(node, "__data__", d)
                        update[i] = node
                    else:
                        enter[i] = EnterNode(parent, d)

                for j, node in enumerate(group):
                    if node is None:
                        continue
                    if node in node_by_key.values():
                        exit_[j] = node

                # Set enter._next to next update node for correct insertion order.
                next_node = None
                for i in range(m - 1, -1, -1):
                    if update[i] is not None:
                        next_node = update[i]
                    elif enter[i] is not None:
                        enter[i]._next = next_node  # type: ignore[union-attr]

            new_groups.append(update)
            new_parents.append(parent)
            enter_groups.append(enter)
            exit_groups.append(exit_)

        return selection(new_groups, new_parents, enter=enter_groups, exit=exit_groups)

    def enter(self) -> "selection":
        if self._enter is None:
            return selection([[]], self._parents)
        return selection(self._enter, self._parents)

    def exit(self) -> "selection":
        if self._exit is None:
            return selection([[]], self._parents)
        return selection(self._exit, self._parents)

    def property(self, name: Any, value: Any = ...):
        key = str(name)
        if value is ...:
            n = self.node()
            if n is None:
                return None
            if isinstance(n, dict):
                return n.get(key)
            if hasattr(n, key):
                return getattr(n, key)
            # jsdom default: checkbox input.checked is false.
            if key == "checked":
                return False
            return None

        def set_one(n, v):  # noqa: ANN001
            if v is None:
                if hasattr(n, key):
                    delattr(n, key)
            else:
                setattr(n, key, v)

        if callable(value):
            for group in self._groups:
                for i, n in enumerate(group):
                    if n is None:
                        continue
                    v = _call_value(value, n, getattr(n, "__data__", None), i, group)
                    set_one(n, v)
        else:
            for group in self._groups:
                for n in group:
                    if n is None:
                        continue
                    set_one(n, value)
        return self

    def text(self, value: Any = ...):
        if value is ...:
            n = self.node()
            if n is None:
                return None
            if isinstance(n, dict):
                return n.get("textContent", "")
            return getattr(n, "textContent", "")

        def set_one(n, v):  # noqa: ANN001
            setattr(n, "textContent", "" if v is None else str(v))

        if callable(value):
            for group in self._groups:
                for i, n in enumerate(group):
                    if n is None:
                        continue
                    set_one(n, _call_value(value, n, getattr(n, "__data__", None), i, group))
        else:
            for group in self._groups:
                for n in group:
                    if n is None:
                        continue
                    set_one(n, value)
        return self

    def html(self, value: Any = ...):
        if value is ...:
            n = self.node()
            if n is None:
                return None
            if isinstance(n, dict):
                return n.get("innerHTML", "")
            return getattr(n, "innerHTML", "")

        def set_one(n, v):  # noqa: ANN001
            setattr(n, "innerHTML", "" if v is None else str(v))

        if callable(value):
            for group in self._groups:
                for i, n in enumerate(group):
                    if n is None:
                        continue
                    set_one(n, _call_value(value, n, getattr(n, "__data__", None), i, group))
        else:
            for group in self._groups:
                for n in group:
                    if n is None:
                        continue
                    set_one(n, value)
        return self

    def classed(self, classes: Any, value: Any = ...):
        cls_list = str(classes).split()
        if value is ...:
            n = self.node()
            if n is None:
                return False
            cur = ""
            if hasattr(n, "getAttribute"):
                cur = n.getAttribute("class") or ""
            have = set(cur.split())
            return all(c in have for c in cls_list)

        def set_one(n, v):  # noqa: ANN001
            cur = ""
            if hasattr(n, "getAttribute"):
                cur = n.getAttribute("class") or ""
            have = set(cur.split())
            on = bool(v)
            for c in cls_list:
                if on:
                    have.add(c)
                else:
                    have.discard(c)
            if hasattr(n, "setAttribute"):
                n.setAttribute("class", " ".join(sorted(have)) if have else "")

        if callable(value):
            for group in self._groups:
                for i, n in enumerate(group):
                    if n is None:
                        continue
                    set_one(n, _call_value(value, n, getattr(n, "__data__", None), i, group))
        else:
            for group in self._groups:
                for n in group:
                    if n is None:
                        continue
                    set_one(n, value)
        return self

    def style(self, name: Any, value: Any = ..., priority: Any = ""):
        key = str(name)
        if value is ...:
            n = self.node()
            if n is None:
                return None
            style_obj = n.get("style") if isinstance(n, dict) else getattr(n, "style", None)
            if style_obj is not None and (
                hasattr(style_obj, "getPropertyValue") or (isinstance(style_obj, dict) and callable(style_obj.get("getPropertyValue")))
            ):
                inline = (
                    style_obj.getPropertyValue(key)
                    if hasattr(style_obj, "getPropertyValue")
                    else style_obj["getPropertyValue"](key)
                )
                if inline:
                    return inline
                # computed style fallback
                owner = n.get("ownerDocument") if isinstance(n, dict) else getattr(n, "ownerDocument", None)
                dv = owner.get("defaultView") if isinstance(owner, dict) else getattr(owner, "defaultView", None) if owner is not None else None
                if dv is not None and (hasattr(dv, "getComputedStyle") or (isinstance(dv, dict) and callable(dv.get("getComputedStyle")))):
                    cs = dv.getComputedStyle(n) if hasattr(dv, "getComputedStyle") else dv["getComputedStyle"](n)
                    if cs is not None:
                        if hasattr(cs, "getPropertyValue"):
                            return cs.getPropertyValue(key)
                        if isinstance(cs, dict) and callable(cs.get("getPropertyValue")):
                            return cs["getPropertyValue"](key)
                        return ""
                return inline
            return None

        def set_one(n, v):  # noqa: ANN001
            style_obj = n.get("style") if isinstance(n, dict) else getattr(n, "style", None)
            if style_obj is None:
                return
            if v is None:
                if hasattr(style_obj, "removeProperty"):
                    style_obj.removeProperty(key)
                elif isinstance(style_obj, dict) and callable(style_obj.get("removeProperty")):
                    style_obj["removeProperty"](key)
            else:
                if hasattr(style_obj, "setProperty"):
                    style_obj.setProperty(key, str(v), str(priority) if priority is not None else "")
                elif isinstance(style_obj, dict) and callable(style_obj.get("setProperty")):
                    style_obj["setProperty"](key, str(v), str(priority) if priority is not None else "")

        if callable(value):
            for group in self._groups:
                for i, n in enumerate(group):
                    if n is None:
                        continue
                    set_one(n, _call_value(value, n, getattr(n, "__data__", None), i, group))
        else:
            for group in self._groups:
                for n in group:
                    if n is None:
                        continue
                    set_one(n, value)
        return self

    def select(self, selector: Any) -> "selection":
        if selector is None:
            def fn(this):  # noqa: ANN001
                return None
        elif callable(selector):
            sel_fn = selector

            def fn(this, d, i, nodes):  # noqa: ANN001
                return _call_value(sel_fn, this, d, i, nodes)
        else:
            sel = str(selector)

            def fn(this, _d, _i, _nodes):  # noqa: ANN001
                return getattr(this, "querySelector")(sel) if this is not None else None

        subgroups: list[list[Any]] = []
        parents: list[Any] = []
        for group, parent in zip(self._groups, self._parents, strict=False):
            subgroup: list[Any] = []
            for i, node in enumerate(group):
                if node is None:
                    subgroup.append(None)
                else:
                    child = fn(node, getattr(node, "__data__", None), i, group)
                    # Propagate bound data only if it exists on originating node.
                    if (
                        child is not None
                        and hasattr(node, "__dict__")
                        and "__data__" in node.__dict__
                        and hasattr(child, "__dict__")
                    ):
                        child.__dict__["__data__"] = node.__dict__["__data__"]
                    subgroup.append(child)
            subgroups.append(subgroup)
            parents.append(parent)
        return selection(subgroups, parents)

    def append(self, name: Any) -> "selection":
        if isinstance(self.node(), EnterNode):
            # Enter selection: insert before next update node.
            make = name if callable(name) else creator(str(name))
            subgroups: list[list[Any]] = []
            for group in self._groups:
                subgroup: list[Any] = []
                for i, en in enumerate(group):
                    if en is None:
                        subgroup.append(None)
                        continue
                    parent = en._parent
                    child = make(parent) if not callable(name) else _call_value(name, en, en.__data__, i, group)
                    if child is None:
                        subgroup.append(None)
                        continue
                    if hasattr(parent, "insertBefore"):
                        parent.insertBefore(child, en._next)
                    elif hasattr(parent, "appendChild"):
                        parent.appendChild(child)
                    if hasattr(child, "__dict__"):
                        child.__dict__["__data__"] = en.__data__
                    subgroup.append(child)
                subgroups.append(subgroup)
            return selection(subgroups, self._parents)

        if callable(name):
            fn = name

            def _create(n, d, i, nodes):  # noqa: ANN001
                return _call_value(fn, n, d, i, nodes)

        else:
            make = creator(str(name))

            def _create(n, _d, _i, _nodes):  # noqa: ANN001
                return make(n)

        subgroups: list[list[Any]] = []
        for group in self._groups:
            subgroup: list[Any] = []
            for i, n in enumerate(group):
                if n is None:
                    subgroup.append(None)
                    continue
                d = getattr(n, "__data__", None)
                child = _create(n, d, i, group)
                if child is None:
                    subgroup.append(None)
                    continue
                if hasattr(n, "appendChild"):
                    n.appendChild(child)
                if hasattr(n, "__dict__") and "__data__" in n.__dict__ and hasattr(child, "__dict__"):
                    child.__dict__["__data__"] = n.__dict__["__data__"]
                subgroup.append(child)
            subgroups.append(subgroup)
        return selection(subgroups, self._parents)

    def insert(self, name: Any, before: Any) -> "selection":
        if isinstance(self.node(), EnterNode):
            # Enter selection insert: before selector resolves against parent.
            make = name if callable(name) else creator(str(name))
            if callable(before):
                before_fn = before

                def _before(parent, d, i, nodes):  # noqa: ANN001
                    return _call_value(before_fn, parent, d, i, nodes)

            elif before is None:
                def _before(_parent, _d, _i, _nodes):  # noqa: ANN001
                    return None
            else:
                sel = str(before)

                def _before(parent, _d, _i, _nodes):  # noqa: ANN001
                    return parent.querySelector(sel) if parent is not None and hasattr(parent, "querySelector") else None

            subgroups: list[list[Any]] = []
            for group in self._groups:
                subgroup: list[Any] = []
                for i, en in enumerate(group):
                    if en is None:
                        subgroup.append(None)
                        continue
                    parent = en._parent
                    child = make(parent) if not callable(name) else _call_value(name, en, en.__data__, i, group)
                    ref = _before(parent, en.__data__, i, group)
                    if hasattr(parent, "insertBefore"):
                        parent.insertBefore(child, ref)
                    elif hasattr(parent, "appendChild"):
                        parent.appendChild(child)
                    if hasattr(child, "__dict__"):
                        child.__dict__["__data__"] = en.__data__
                    subgroup.append(child)
                subgroups.append(subgroup)
            return selection(subgroups, self._parents)

        if callable(before):
            before_fn = before

            def _before(n, d, i, nodes):  # noqa: ANN001
                return _call_value(before_fn, n, d, i, nodes)

        else:
            sel = str(before)

            def _before(n, _d, _i, _nodes):  # noqa: ANN001
                return n.querySelector(sel) if n is not None and hasattr(n, "querySelector") else None

        if callable(name):
            create_fn = name

            def _create(n, d, i, nodes):  # noqa: ANN001
                return _call_value(create_fn, n, d, i, nodes)

        else:
            make = creator(str(name))

            def _create(n, _d, _i, _nodes):  # noqa: ANN001
                return make(n)

        subgroups: list[list[Any]] = []
        for group in self._groups:
            subgroup: list[Any] = []
            for i, n in enumerate(group):
                if n is None:
                    subgroup.append(None)
                    continue
                d = getattr(n, "__data__", None)
                child = _create(n, d, i, group)
                if child is None:
                    subgroup.append(None)
                    continue
                ref = _before(n, d, i, group)
                if hasattr(n, "insertBefore"):
                    n.insertBefore(child, ref)
                elif hasattr(n, "appendChild"):
                    n.appendChild(child)
                subgroup.append(child)
            subgroups.append(subgroup)
        return selection(subgroups, self._parents)

    def remove(self) -> "selection":
        for group in self._groups:
            for n in group:
                if n is None:
                    continue
                parent = getattr(n, "parentNode", None)
                if parent is None:
                    continue
                if hasattr(parent, "removeChild"):
                    try:
                        parent.removeChild(n)
                    except ValueError:
                        # Already detached.
                        pass
        return self

    def selectChildren(self, match: Any = None) -> "selection":
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
                    kids = [c for c in kids if hasattr(c, "querySelectorAll") and c in c.parentNode.querySelectorAll(sel)]
                subgroups.append(kids)
                parents.append(n)
        return selection(subgroups, parents)

    def selectChild(self, match: Any = None) -> "selection":
        if match is None:
            match = "*"

        if callable(match):
            fn = match

            def _pick(n, d, i, nodes):  # noqa: ANN001
                # find first child for which fn returns truthy
                for c in getattr(n, "childNodes", []):
                    if _call_value(fn, c, getattr(c, "__data__", None), 0, [c]):
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

    def join(self, enter: Any, update: Any = None, exit: Any = None):
        # join(name) shorthand
        if isinstance(enter, str):
            name = enter

            def enter_fn(e):  # noqa: ANN001
                return e.append(name)

            def update_fn(u):  # noqa: ANN001
                return u

            def exit_fn(x):  # noqa: ANN001
                x.remove()
                return x

            enter, update, exit = enter_fn, update_fn, exit_fn

        ent = self.enter()
        upd = self
        ext = self.exit()

        ent_out = enter(ent) if callable(enter) else ent
        upd_out = upd if update is None else update(upd)
        ext_out = None if exit is None else exit(ext)

        if hasattr(ent_out, "selection") and callable(ent_out.selection):
            ent_out = ent_out.selection()
        if hasattr(upd_out, "selection") and callable(upd_out.selection):
            upd_out = upd_out.selection()
        if ext_out is not None and hasattr(ext_out, "selection") and callable(ext_out.selection):
            ext_out = ext_out.selection()

        # Ensure exit nodes remain in DOM (for transition-style patterns), but
        # order update+enter nodes to match data order.
        merged = ent_out.merge(upd_out).order()
        if ext_out is not None:
            return ext_out.merge(merged)
        return merged

    def selectAll(self, selector: Any) -> "selection":
        if selector is None:
            def fn(this):  # noqa: ANN001
                return []
        elif callable(selector):
            sel_fn = selector

            def fn(this, d, i, nodes):  # noqa: ANN001
                return _call_value(sel_fn, this, d, i, nodes) or []
        else:
            sel = str(selector)

            def fn(this, _d, _i, _nodes):  # noqa: ANN001
                return getattr(this, "querySelectorAll")(sel) if this is not None else []

        subgroups: list[list[Any]] = []
        parents: list[Any] = []
        for group, parent in zip(self._groups, self._parents, strict=False):
            for i, node in enumerate(group):
                if node is None:
                    continue
                d = getattr(node, "__data__", None)
                subgroups.append(list(fn(node, d, i, group)))
                parents.append(node)
        return selection(subgroups, parents)

    def attr(self, name: Any, value: Any = ...):
        key = _namespace(name)
        if isinstance(key, dict):
            uri = key["space"]
            local = key["local"]
        else:
            uri = None
            local = str(key)

        if value is ...:
            n = self.node()
            if n is None:
                return None
            if uri is None:
                if isinstance(n, dict) and callable(n.get("getAttribute")):
                    return n["getAttribute"](local)
                return n.getAttribute(local) if hasattr(n, "getAttribute") else None
            if isinstance(n, dict) and callable(n.get("getAttributeNS")):
                return n["getAttributeNS"](uri, local)
            return n.getAttributeNS(uri, local) if hasattr(n, "getAttributeNS") else None

        def set_one(n, v):  # noqa: ANN001
            if uri is None:
                if v is None:
                    if isinstance(n, dict) and callable(n.get("removeAttribute")):
                        n["removeAttribute"](local)
                    elif hasattr(n, "removeAttribute"):
                        n.removeAttribute(local)
                else:
                    if isinstance(n, dict) and callable(n.get("setAttribute")):
                        n["setAttribute"](local, str(v))
                    elif hasattr(n, "setAttribute"):
                        n.setAttribute(local, str(v))
            else:
                if v is None:
                    if isinstance(n, dict) and callable(n.get("removeAttributeNS")):
                        n["removeAttributeNS"](uri, local)
                    elif hasattr(n, "removeAttributeNS"):
                        n.removeAttributeNS(uri, local)
                else:
                    if isinstance(n, dict) and callable(n.get("setAttributeNS")):
                        n["setAttributeNS"](uri, local, str(v))
                    elif hasattr(n, "setAttributeNS"):
                        n.setAttributeNS(uri, local, str(v))

        if callable(value):
            for group in self._groups:
                for i, n in enumerate(group):
                    if n is None:
                        continue
                    v = _call_value(value, n, getattr(n, "__data__", None), i, group)
                    set_one(n, v)
        else:
            for group in self._groups:
                for n in group:
                    if n is None:
                        continue
                    set_one(n, value)
        return self

    def __iter__(self) -> Iterator[Any]:
        return iter(self.nodes())


Selection = selection

