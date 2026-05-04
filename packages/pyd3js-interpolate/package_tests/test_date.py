from __future__ import annotations

from datetime import datetime

from pyd3js_interpolate import interpolateDate


def test_interpolate_date() -> None:
    a = datetime(2000, 1, 1)
    b = datetime(2000, 1, 2)
    i = interpolateDate(a, b)
    mid = i(0.5)
    assert mid == datetime(2000, 1, 1, 12)
