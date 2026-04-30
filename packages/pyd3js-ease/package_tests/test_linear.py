from __future__ import annotations

import math

from pyd3js_ease import easeLinear


def test_ease_linear_basic() -> None:
    assert easeLinear(0.0) == 0.0
    assert math.isclose(easeLinear(0.1), 0.1)
    assert easeLinear(1.0) == 1.0


def test_ease_linear_coerces() -> None:
    assert easeLinear(".9") == easeLinear(0.9)

    class _V:
        def valueOf(self) -> float:
            return 0.9

    assert easeLinear(_V()) == easeLinear(0.9)
