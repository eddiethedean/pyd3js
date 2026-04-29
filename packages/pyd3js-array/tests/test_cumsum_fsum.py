from __future__ import annotations

import math

import pytest

from pyd3js_array.cumsum import cumsum
from pyd3js_array.fsum import Adder, fcumsum, fsum


def test_cumsum_coerces_and_treats_invalid_as_zero() -> None:
    assert cumsum([None, "2", 3, "nope", True, 0]) == [0.0, 2.0, 5.0, 5.0, 6.0, 6.0]


def test_fsum_has_better_precision_than_naive_sum() -> None:
    values = [1e16, 1.0, -1e16, 1.0]
    assert fsum(values) == math.fsum(values)
    assert fsum(values) == 2.0


def test_fsum_skips_zeros_like_upstream() -> None:
    assert fsum([0, 0.0, -0.0]) == 0.0


def test_adder_matches_fsum_result() -> None:
    a = Adder()
    a.add(1e16).add(1.0).add(-1e16)
    assert float(a) == 1.0


def test_fcumsum_matches_cumsum_on_simple_inputs() -> None:
    assert fcumsum([1, 2, 3]) == [1.0, 3.0, 6.0]


@pytest.mark.oracle
def test_cumsum_fsum_fcumsum_match_oracle(require_oracle: None) -> None:
    from tests.oracle.client import assert_approx_oracle, oracle_eval

    assert cumsum([None, "2", 3, "nope", True, 0]) == oracle_eval(
        "(function(){ return Array.from(d3.cumsum([null,'2',3,'nope',true,0])); })()"
    )

    assert_approx_oracle(
        fsum([1e16, 1.0, -1e16]),
        "(function(){ return d3.fsum([1e16,1,-1e16]); })()",
    )

    js = oracle_eval("(function(){ return Array.from(d3.fcumsum([1e16,1,-1e16])); })()")
    py = fcumsum([1e16, 1.0, -1e16])
    assert len(py) == len(js)
    for a, b in zip(py, js):
        assert math.isclose(a, b, rel_tol=1e-12, abs_tol=1e-12)

