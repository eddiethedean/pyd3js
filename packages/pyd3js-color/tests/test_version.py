from __future__ import annotations

import re
from pathlib import Path

import pyd3js_color


def test_version_matches_pyproject() -> None:
    """Keep __version__ aligned with [project].version for releases."""
    pyproject = Path(__file__).resolve().parents[1].joinpath("pyproject.toml")
    text = pyproject.read_text(encoding="utf-8")
    m = re.search(r'(?m)^version\s*=\s*"([^"]+)"\s*$', text)
    assert m is not None
    assert pyd3js_color.__version__ == m.group(1)
