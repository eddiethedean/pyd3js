"""Direct coverage for `_util` helpers not exercised elsewhere."""

from __future__ import annotations

from pyrobust_predicates._util import negate, sum_three


def test_sum_three_merges_three_expansions() -> None:
    a = [1.0]
    b = [2.0]
    c = [4.0]
    tmp = [0.0] * 32
    out = [0.0] * 32
    n = sum_three(1, a, 1, b, 1, c, tmp, out)
    assert n >= 1
    assert abs(sum(out[:n]) - 7.0) < 1e-14


def test_negate_in_place() -> None:
    e = [1.0, -2.0, 3.5]
    assert negate(3, e) == 3
    assert e == [-1.0, 2.0, -3.5]
