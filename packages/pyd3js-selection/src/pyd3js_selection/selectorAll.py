from __future__ import annotations

from collections.abc import Callable

from pyd3js_selection._dom import Element


def selectorAll(selector: str | None = None) -> Callable[[Element], list[Element]]:
    if selector is None:

        def _empty(this: Element | None = None) -> list[Element]:  # noqa: ARG001
            return []

        return _empty

    def _sel(this: Element) -> list[Element]:
        return this.querySelectorAll(str(selector))

    return _sel
