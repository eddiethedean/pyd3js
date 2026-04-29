from __future__ import annotations

import pytest


@pytest.mark.oracle
def test_oracle_eval_extent(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    assert list(oracle_eval("(function(){ return d3.extent([1,2,3]); })()")) == [1, 3]
