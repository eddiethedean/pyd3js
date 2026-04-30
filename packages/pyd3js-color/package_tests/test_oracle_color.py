from __future__ import annotations

import pytest


@pytest.mark.oracle
def test_oracle_color_formatters_json_safe(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    import pyd3js_color as c

    steel = c.color("steelblue")
    assert steel is not None
    assert steel.formatRgb() == oracle_eval(
        '(function(){ return d3.color("steelblue").formatRgb(); })()'
    )
    assert c.rgb(70, 130, 180).formatHex() == oracle_eval(
        "(function(){ return d3.rgb(70, 130, 180).formatHex(); })()"
    )
    assert c.hsl(120, 0.5, 0.5).formatHsl() == oracle_eval(
        "(function(){ return d3.hsl(120, 0.5, 0.5).formatHsl(); })()"
    )
    assert c.lab(50, 10, -20).formatRgb() == oracle_eval(
        "(function(){ return d3.lab(50, 10, -20).formatRgb(); })()"
    )
    assert c.gray(0.5).formatRgb() == oracle_eval(
        "(function(){ return d3.gray(0.5).formatRgb(); })()"
    )
    assert c.hcl(120, 50, 50).formatRgb() == oracle_eval(
        "(function(){ return d3.hcl(120, 50, 50).formatRgb(); })()"
    )
    assert c.lch(50, 50, 120).formatRgb() == oracle_eval(
        "(function(){ return d3.lch(50, 50, 120).formatRgb(); })()"
    )
    assert c.cubehelix(300, 0.5, 0.5).formatRgb() == oracle_eval(
        "(function(){ return d3.cubehelix(300, 0.5, 0.5).formatRgb(); })()"
    )
