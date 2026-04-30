"""d3 `enter` node: insert before / append like d3 selection enter."""

from __future__ import annotations

from ._svg import Element


class EnterNode:
    """A placeholder in the data join: insert into parent before next sibling (d3)."""

    __slots__ = ("_parent", "__data__", "_next", "_key")

    def __init__(self, parent: Element, datum: object, key: str | None) -> None:
        self._parent = parent
        self.__data__ = datum
        self._next: Element | None = None
        self._key = key

    def __repr__(self) -> str:  # pragma: no cover
        return f"<EnterNode parent={self._parent.tag!r}>"

    @property
    def parent(self) -> Element:
        return self._parent

    @property
    def next_sibling(self) -> Element | None:
        return self._next

    @next_sibling.setter
    def next_sibling(self, n: Element | None) -> None:
        self._next = n

    def querySelector(self, sel: str) -> Element | None:  # noqa: N802
        return self._parent.query_selector(sel) if self._parent else None

    def querySelectorAll(self, sel: str) -> list[Element]:  # noqa: N802
        return self._parent.query_selector_all(sel) if self._parent else []

    def appendChild(self, el: Element) -> Element:  # noqa: N802
        return self._parent.append_child(el)

    def insertBefore(self, new_child: Element, before: Element | None) -> Element:  # noqa: N802
        return self._parent.insert_before(new_child, self._next or before)
