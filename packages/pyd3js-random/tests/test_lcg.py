from __future__ import annotations

import pytest

from pyd3js_random import lcg


@pytest.mark.oracle
def test_lcg_matches_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    gen = lcg(0.5)
    seq = [gen() for _ in range(5)]
    js = oracle_eval(
        "(function(){ const r = d3.randomLcg(0.5); return [r(),r(),r(),r(),r()]; })()"
    )
    assert len(seq) == len(js)
    for a, b in zip(seq, js):
        assert abs(a - b) < 1e-15, (a, b)
