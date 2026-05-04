from __future__ import annotations

import pyd3js_ease as m
from pyd3js_ease_pt.ease_testutil import assert_in_delta


def test_ease_linear_basic() -> None:
    assert m.easeLinear(0.0) == 0.0
    for x in (0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9):
        assert_in_delta(m.easeLinear(x), x)
    assert m.easeLinear(1.0) == 1.0


def test_ease_linear_coerces() -> None:
    assert m.easeLinear(".9") == m.easeLinear(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert m.easeLinear(_V()) == m.easeLinear(0.9)
