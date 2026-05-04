from __future__ import annotations

from collections.abc import Callable
from typing import Optional

from pyd3js_selection._dom import Element


def selector(selector: str | None = None) -> Callable[[Element], Optional[Element]]:
    if selector is None:

        def _undef(this: Element) -> Optional[Element]:  # noqa: ARG001
            return None

        return _undef

    def _sel(this: Element) -> Optional[Element]:
        return this.querySelector(str(selector))

    return _sel
