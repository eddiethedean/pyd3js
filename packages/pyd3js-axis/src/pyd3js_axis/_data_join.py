"""d3-selection data-join: `bindIndex` + `bindKey` + enter `_next` wiring (data.js)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, cast

from ._enter import EnterNode
from ._svg import Element

# Used for Selection groups (Element, EnterNode, or None)
Node = Any

__all__ = (
    "bind_index",
    "bind_key",
    "connect_enter_next",
)


def _parent_element(parent: object) -> Element:
    if isinstance(parent, EnterNode):
        return parent._parent
    if not isinstance(parent, Element):
        raise TypeError(  # pragma: no cover
            "data join parent must be an Element (d3: selectAll’s parent list)"
        )
    return parent


def _key_to_str(datum_key: object) -> str:
    if isinstance(datum_key, (int, float)) and (
        not isinstance(datum_key, float) or datum_key == datum_key
    ):
        return str((+datum_key))
    return str(datum_key)


def _key_key(key: Callable[..., object], datum: object) -> str:
    """A D3 *scale* used as key: only the datum (first `call` arg) matters (d3-axis)."""
    v = key(datum)  # d3: key.call(this, a0, a1, a2) — a scale only reads a0
    return _key_to_str(v)  # type: ignore[operator, misc, call-arg]


def bind_index(
    parent: object,
    group: list[Node | None],
    data: list[object],
) -> tuple[list[Node | None], list[EnterNode | None], list[Node | None]]:
    p_el = _parent_element(parent)
    data_length = len(data)
    group_length = len(group)
    enter: list[EnterNode | None] = [None] * data_length
    update: list[Node | None] = [None] * data_length
    ex: list[Node | None] = [None] * group_length
    for i in range(data_length):
        node = group[i] if i < group_length else None
        if node is not None and not isinstance(node, EnterNode):
            node.__data__ = data[i]  # type: ignore[union-attr, assignment, attr-defined]
            update[i] = node
        else:
            enter[i] = EnterNode(p_el, data[i], None)  # type: ignore[assignment, call-arg, misc]
    for j in range(data_length, group_length):
        n2 = group[j] if j < group_length else None
        if n2 is not None and not isinstance(n2, EnterNode):
            ex[j] = n2
    return update, enter, ex


def bind_key(
    parent: object,
    group: list[Node | None],
    data: list[object],
    key: Callable[..., object],
) -> tuple[list[Node | None], list[EnterNode | None], list[Node | None]]:
    """d3 `bindKey` (see d3-selection/src/selection/data.js)."""
    p_el = _parent_element(parent)
    data_len = len(data)
    group_len = len(group)
    node_by_key: dict[str, Element] = {}
    key_values: list[str] = [""] * group_len
    ex: list[Node | None] = [None] * group_len

    for i in range(group_len):
        node = group[i]
        if node is not None and not isinstance(node, EnterNode):
            n = cast(Element, node)
            k = _key_key(key, n.__data__)
            if k in node_by_key and node_by_key[k] is not None:
                ex[i] = n
            else:
                node_by_key[k] = n
            key_values[i] = k
        else:
            key_values[i] = ""

    update: list[Node | None] = [None] * data_len
    enter: list[EnterNode | None] = [None] * data_len
    for i2 in range(data_len):
        kv2 = _key_key(key, data[i2])
        n2 = node_by_key.get(kv2)
        if n2 is not None:
            n2.__data__ = data[i2]  # type: ignore[union-attr, assignment, attr-defined]
            update[i2] = n2
            del node_by_key[kv2]
        else:
            enter[i2] = EnterNode(p_el, data[i2], None)  # type: ignore[assignment, call-arg, misc]

    for i3 in range(group_len):
        node3 = group[i3] if i3 < group_len else None
        if not node3 or isinstance(node3, EnterNode) or not i3 < len(key_values):
            continue
        kv3 = key_values[i3]
        n3 = cast(Element, node3)
        if kv3 and node_by_key.get(kv3) is n3:
            ex[i3] = n3
    return update, enter, ex


def connect_enter_next(
    enter: list[EnterNode | None],
    update: list[Node | None],
) -> None:
    """Wiring from d3 `data.js` (post-bind): `enterGroup[i0]._next = first update >= i0+1` etc."""
    data_len = len(enter)
    i0 = 0
    i1 = 0
    while i0 < data_len:
        previous = enter[i0]
        if previous is not None and isinstance(previous, EnterNode):
            if i0 >= i1:
                i1 = i0 + 1
            nxt: Node | None = None
            while i1 < data_len:
                nxt = update[i1]
                if nxt is not None and not isinstance(nxt, EnterNode):
                    break
                i1 += 1
            previous._next = nxt if isinstance(nxt, Element) else None
        i0 += 1
