from __future__ import annotations

import pytest

import pyd3js_chord as c
from tests.oracle.client import oracle_eval

from .asserts import assert_in_delta


@pytest.mark.oracle
def test_oracle_chord_defaults(require_oracle: None) -> None:
    matrix = [
        [11975, 5871, 8916, 2868],
        [1951, 10048, 2060, 6171],
        [8010, 16145, 8090, 8045],
        [1013, 990, 940, 6907],
    ]

    py = c.chord()(matrix)
    js = oracle_eval(f"(function(){{ return d3.chord()({matrix}); }})()")

    # Oracle returns an Array with a `.groups` property; through JSON it comes back as a list
    # and we can compute groups separately for comparison.
    js_groups = oracle_eval(f"(function(){{ return d3.chord()({matrix}).groups; }})()")

    assert_in_delta(py.groups, js_groups)
    assert_in_delta(py, js)


@pytest.mark.oracle
def test_oracle_ribbon_path_string(require_oracle: None) -> None:
    d = {
        "source": {"startAngle": 0.0, "endAngle": 1.0, "radius": 100.0},
        "target": {"startAngle": 2.0, "endAngle": 2.5, "radius": 80.0},
    }

    py = c.ribbon()(d)
    assert py is not None

    js = oracle_eval(f"(function(){{ const r = d3.ribbon(); return r({d})}})()")
    assert js is not None

    # Allow tiny float formatting differences; compare numbers normalized to 1e-6 like upstream tests.
    import re

    re_number = re.compile(r"[-+]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:[eE][-]?\d+)?")

    def normalize_path(path: str) -> str:
        def format_number(m: re.Match[str]) -> str:
            s = float(m.group(0))
            if abs(s - round(s)) < 1e-6:
                return str(int(round(s)))
            return f"{s:.6f}"

        return re_number.sub(format_number, path)

    assert normalize_path(py) == normalize_path(js)
