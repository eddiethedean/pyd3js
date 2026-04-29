from __future__ import annotations

import pyd3js


def test_umbrella_lazy_modules() -> None:
    m = pyd3js.array
    assert m.extent([1, 2, 3]) == (1, 3)
