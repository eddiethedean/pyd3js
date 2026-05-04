from __future__ import annotations

from pyd3js_selection.selection.index import selection as _Selection
from pyd3js_transition.selection.interrupt import selection_interrupt
from pyd3js_transition.selection.transition import selection_transition


def _patch_selection() -> None:
    # Mirror d3-transition’s side-effect import that patches selection.prototype.
    setattr(_Selection, "interrupt", selection_interrupt)
    setattr(_Selection, "transition", selection_transition)


_patch_selection()

