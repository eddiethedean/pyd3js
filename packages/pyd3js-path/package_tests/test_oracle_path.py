from __future__ import annotations

import math
import re

import pytest

import pyd3js_path as p
from tests.oracle.client import oracle_eval

_RE_NUMBER = re.compile(r"[-+]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:[eE][-]?\d+)?")


def _format_number(m: re.Match[str]) -> str:
    s = float(m.group(0))
    if abs(s - round(s)) < 1e-6:
        return str(int(round(s)))
    return f"{s:.6f}"


def normalize_path(d: str) -> str:
    return _RE_NUMBER.sub(_format_number, d)


@pytest.mark.oracle
def test_oracle_path_basic_commands(require_oracle: None) -> None:
    py = p.path()
    py.moveTo(150, 50)
    py.lineTo(200, 100)
    py.quadraticCurveTo(100, 50, 200, 100)
    py.bezierCurveTo(100, 50, 0, 24, 200, 100)
    py.rect(100, 200, 50, 25)
    py.closePath()

    js = oracle_eval(
        "(function(){"
        "  const p = d3.path();"
        "  p.moveTo(150, 50);"
        "  p.lineTo(200, 100);"
        "  p.quadraticCurveTo(100, 50, 200, 100);"
        "  p.bezierCurveTo(100, 50, 0, 24, 200, 100);"
        "  p.rect(100, 200, 50, 25);"
        "  p.closePath();"
        "  return p + '';"
        "})()"
    )

    assert normalize_path(str(py)) == normalize_path(js)


@pytest.mark.oracle
def test_oracle_arc_variants(require_oracle: None) -> None:
    py = p.path()
    py.moveTo(150, 100)
    py.arc(100, 100, 50, 0, math.pi / 2, False)
    py.arc(100, 100, 50, 0, 2 * math.pi, True)
    py.arc(100, 100, 50, 0, -1e-16, False)

    js = oracle_eval(
        "(function(){"
        "  const p = d3.path();"
        "  p.moveTo(150, 100);"
        "  p.arc(100, 100, 50, 0, Math.PI / 2, false);"
        "  p.arc(100, 100, 50, 0, 2 * Math.PI, true);"
        "  p.arc(100, 100, 50, 0, -1e-16, false);"
        "  return p + '';"
        "})()"
    )
    assert normalize_path(str(py)) == normalize_path(js)


@pytest.mark.oracle
def test_oracle_arc_to_variants(require_oracle: None) -> None:
    py = p.path()
    py.moveTo(270, 182)
    py.arcTo(270, 39, 163, 100, 53)
    py.arcTo(270, 39, 363, 100, 53)
    py.moveTo(100, 100)
    py.arcTo(200, 100, 200, 200, 50)

    js = oracle_eval(
        "(function(){"
        "  const p = d3.path();"
        "  p.moveTo(270, 182);"
        "  p.arcTo(270, 39, 163, 100, 53);"
        "  p.arcTo(270, 39, 363, 100, 53);"
        "  p.moveTo(100, 100);"
        "  p.arcTo(200, 100, 200, 200, 50);"
        "  return p + '';"
        "})()"
    )
    assert normalize_path(str(py)) == normalize_path(js)


@pytest.mark.oracle
def test_oracle_path_round(require_oracle: None) -> None:
    py = p.pathRound(1)
    py.moveTo(math.pi, math.e)
    py.arc(10.0001, 10.0001, 123.456, 0, math.pi + 0.0001)
    py.arcTo(10.0001, 10.0001, 123.456, 456.789, 12345.6789)
    py.rect(10.0001, 10.0001, 123.456, 456.789)

    js = oracle_eval(
        "(function(){"
        "  const p = d3.pathRound(1);"
        "  p.moveTo(Math.PI, Math.E);"
        "  p.arc(10.0001, 10.0001, 123.456, 0, Math.PI + 0.0001);"
        "  p.arcTo(10.0001, 10.0001, 123.456, 456.789, 12345.6789);"
        "  p.rect(10.0001, 10.0001, 123.456, 456.789);"
        "  return p + '';"
        "})()"
    )
    assert normalize_path(str(py)) == normalize_path(js)

