from __future__ import annotations

from typing import Any

from pyd3js_selection.selection.index import selection as _Selection


def transition_selection(self) -> Any:  # noqa: ANN001
    # d3: transition.selection() -> selection
    return _Selection(self._groups, self._parents)

