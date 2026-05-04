from __future__ import annotations

from typing import Any

from pyd3js_transition.interrupt import interrupt


def selection_interrupt(self, name: Any = None):  # noqa: ANN001
    # d3: selection.prototype.interrupt = function(name) { return this.each(...); }
    return self.each(lambda node, *_: interrupt(node, name))

