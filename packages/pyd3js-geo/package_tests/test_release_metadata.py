"""Release hygiene: version string matches packaging metadata."""

from __future__ import annotations

import re
from pathlib import Path

import pyd3js_geo


def test_version_matches_pyproject() -> None:
    pkg_root = Path(pyd3js_geo.__file__).resolve().parents[2]
    text = (pkg_root / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'^version = "([^"]+)"\s*$', text, re.MULTILINE)
    assert m is not None
    assert pyd3js_geo.__version__ == m.group(1)


def test_version_pep440_semver_patch() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", pyd3js_geo.__version__) is not None
