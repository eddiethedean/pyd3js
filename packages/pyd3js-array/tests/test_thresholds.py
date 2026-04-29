from __future__ import annotations

import pytest

from pyd3js_array.threshold_freedman_diaconis import thresholdFreedmanDiaconis
from pyd3js_array.threshold_scott import thresholdScott
from pyd3js_array.threshold_sturges import thresholdSturges


def test_threshold_sturges_basic() -> None:
    assert thresholdSturges([1, 2, 3, 4, 5, 6, 7, 8]) == 4


def test_thresholds_return_positive_ints() -> None:
    data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert thresholdFreedmanDiaconis(data, 1, 9) >= 1
    assert thresholdScott(data, 1, 9) >= 1


@pytest.mark.oracle
def test_thresholds_match_oracle(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    data = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert thresholdSturges(data) == oracle_eval(
        "(function(){ return d3.thresholdSturges([1,2,3,4,5,6,7,8,9]); })()"
    )
    assert thresholdScott(data, 1, 9) == oracle_eval(
        "(function(){ return d3.thresholdScott([1,2,3,4,5,6,7,8,9], 1, 9); })()"
    )
    assert thresholdFreedmanDiaconis(data, 1, 9) == oracle_eval(
        "(function(){ return d3.thresholdFreedmanDiaconis([1,2,3,4,5,6,7,8,9], 1, 9); })()"
    )
