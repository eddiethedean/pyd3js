from __future__ import annotations

import json

import pytest

from pyd3js_array.bisect import bisectCenter, bisectLeft, bisectRight
from pyd3js_array.bisector import _is_accessor, bisector
from typing import Any, Callable, cast


def test_bisect_left_right_duplicates() -> None:
    a = [1, 2, 2, 2, 3]
    assert bisectLeft(a, 2) == 1
    assert bisectRight(a, 2) == 4


def test_bisect_center_examples() -> None:
    a = [1, 2, 2, 2, 3]
    assert bisectCenter(a, 2) == 1
    assert bisectCenter(a, 2.4) == 3
    assert bisectCenter(a, 2.6) == 4
    assert bisectCenter(a, 0) == 0
    assert bisectCenter(a, 10) == 4


def test_bisect_lo_hi() -> None:
    assert bisectLeft([1, 2, 3], 2, 1, 2) == 1


def test_bisector_accessor() -> None:
    b = bisector(lambda d: d["v"])
    a = [{"v": 1}, {"v": 2}, {"v": 2}, {"v": 3}]
    assert b.left(a, 2) == 1
    assert b.right(a, 2) == 3
    assert b.center(a, 2.6) == 3


def test_bisector_comparator() -> None:
    b = bisector(lambda a, b: a - b)
    assert b.left([1, 2, 3], 2) == 1
    assert b.right([1, 2, 3], 2) == 2


def test_is_accessor_fallback() -> None:
    assert _is_accessor(cast(Callable[..., Any], object())) is False


@pytest.mark.oracle
def test_bisect_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases = [
        ([1, 2, 2, 2, 3], 2),
        ([1, 2, 3], 2),
        ([1, 2, 2, 2, 3], 2.4),
    ]
    for arr, x in cases:
        py_l = bisectLeft(list(arr), x)
        py_r = bisectRight(list(arr), x)
        py_c = bisectCenter(list(arr), x)
        js_l = oracle_eval(
            f"(function(){{ return d3.bisectLeft({json.dumps(arr)}, {json.dumps(x)}); }})()"
        )
        js_r = oracle_eval(
            f"(function(){{ return d3.bisectRight({json.dumps(arr)}, {json.dumps(x)}); }})()"
        )
        js_c = oracle_eval(
            f"(function(){{ return d3.bisectCenter({json.dumps(arr)}, {json.dumps(x)}); }})()"
        )
        assert (py_l, py_r, py_c) == (js_l, js_r, js_c)


@pytest.mark.oracle
def test_bisector_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    data = [{"v": 1}, {"v": 2}, {"v": 2}, {"v": 3}]
    b = bisector(lambda d: d["v"])
    assert b.left(data, 2) == oracle_eval(
        f"(function(){{ return d3.bisector(d => d.v).left({json.dumps(data)}, 2); }})()"
    )
    assert b.right(data, 2) == oracle_eval(
        f"(function(){{ return d3.bisector(d => d.v).right({json.dumps(data)}, 2); }})()"
    )
