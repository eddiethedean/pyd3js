from __future__ import annotations

from collections.abc import Callable

from pyd3js_selection._dom import Element


def matcher(selector: str) -> Callable[[Element], bool]:
    def _m(this: Element) -> bool:
        sel = str(selector)
        if sel.startswith("#"):
            return this.getAttribute("id") == sel[1:]
        if sel.startswith("."):
            cls = this.getAttribute("class") or ""
            return sel[1:] in cls.split()
        if "." in sel:
            tag, cls = sel.split(".", 1)
            if this.tagName.lower() != tag.lower():
                return False
            classes = this.getAttribute("class") or ""
            return cls in classes.split()
        return this.tagName.lower() == sel.lower()

    return _m

