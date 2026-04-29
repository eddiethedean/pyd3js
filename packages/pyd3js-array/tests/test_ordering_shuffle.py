from __future__ import annotations

import math

import pytest

from pyd3js_array.ascending import ascending
from pyd3js_array.descending import descending
from pyd3js_array.shuffle import shuffle
from pyd3js_array.shuffler import shuffler


def test_ascending_descending_basic() -> None:
    assert ascending(1, 2) == -1
    assert ascending(2, 1) == 1
    assert ascending(1, 1) == 0

    assert descending(1, 2) == 1
    assert descending(2, 1) == -1
    assert descending(1, 1) == 0


def test_ascending_descending_nan() -> None:
    assert math.isnan(ascending(float("nan"), 1))
    assert math.isnan(ascending(1, float("nan")))
    assert math.isnan(descending(float("nan"), 1))
    assert math.isnan(descending(1, float("nan")))


def test_ascending_descending_strings() -> None:
    assert ascending("2", "10") == 1
    assert ascending("10", "2") == -1
    assert ascending("a", "a") == 0
    assert descending("2", "10") == -1
    assert descending("a", "a") == 0


def test_shuffle_properties() -> None:
    a = [1, 2, 3, 4, 5]
    out = shuffle(a)
    assert out is a
    assert sorted(out) == [1, 2, 3, 4, 5]


def test_shuffle_range_only() -> None:
    a = [1, 2, 3, 4, 5]
    shuffle(a, 1, 4)
    assert a[0] == 1
    assert a[4] == 5
    assert sorted(a[1:4]) == [2, 3, 4]


def test_shuffler_deterministic() -> None:
    # Deterministic RNG that cycles a fixed sequence.
    seq = [0.9, 0.1, 0.5, 0.3, 0.7]
    it = iter(seq)

    def rng() -> float:
        return next(it)

    s = shuffler(rng)
    a = [1, 2, 3, 4, 5]
    s(a, 0, 5)
    assert a == [3, 4, 2, 1, 5]


@pytest.mark.oracle
def test_ascending_descending_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    cases = [
        (1, 2),
        (2, 1),
        (1, 1),
        ("2", "10"),
        ("10", "2"),
    ]
    for a, b in cases:
        js_a = oracle_eval(f"(function(){{ return d3.ascending({a!r}, {b!r}); }})()")
        js_d = oracle_eval(f"(function(){{ return d3.descending({a!r}, {b!r}); }})()")
        assert ascending(a, b) == js_a
        assert descending(a, b) == js_d


@pytest.mark.oracle
def test_shuffler_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    expr = r"""(function(){
  const seq = [0.9, 0.1, 0.5, 0.3, 0.7];
  let i = 0;
  function rng(){ return seq[i++]; }
  const a = [1,2,3,4,5];
  d3.shuffler(rng)(a, 0, 5);
  return a;
})()"""
    js = oracle_eval(expr)

    seq = [0.9, 0.1, 0.5, 0.3, 0.7]
    it = iter(seq)

    def rng() -> float:
        return next(it)

    a = [1, 2, 3, 4, 5]
    shuffler(rng)(a, 0, 5)
    assert a == js

