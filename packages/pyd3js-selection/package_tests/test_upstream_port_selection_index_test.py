from __future__ import annotations

import pyd3js_selection as s


def test_selection_returns_selection_of_document_element(jsdom):
    doc = jsdom("")
    assert s.selection().node() is doc.documentElement


def test_selection_prototype_can_be_extended(jsdom):
    doc = jsdom("<input type='checkbox'>")
    sel = s.select(doc.querySelector("[type=checkbox]"))

    def checked(self: s.Selection, value=...):
        return self.property("checked", bool(value)) if value is not ... else self.property("checked")

    try:
        setattr(s.selection, "checked", checked)  # type: ignore[attr-defined]
        assert sel.checked() is False  # type: ignore[attr-defined]
        assert sel.checked(True) is sel  # type: ignore[attr-defined]
        assert sel.checked() is True  # type: ignore[attr-defined]
    finally:
        if hasattr(s.selection, "checked"):
            delattr(s.selection, "checked")


def test_selection_returns_instanceof_selection(jsdom):
    jsdom("")
    assert isinstance(s.selection(), s.selection)

