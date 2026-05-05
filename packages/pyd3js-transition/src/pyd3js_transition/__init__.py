"""
pyd3js-transition — Python port of d3-transition.
"""

from __future__ import annotations

# Side-effect import to extend pyd3js-selection with `.transition` / `.interrupt`.
from pyd3js_transition.selection.index import _patch_selection  # noqa: F401
from pyd3js_transition.transition.index import Transition, new_id, transition
from pyd3js_transition.active import active
from pyd3js_transition.interrupt import interrupt

__version__ = "0.1.0"

__all__ = [
    "Transition",
    "__version__",
    "active",
    "interrupt",
    "new_id",
    "transition",
]
