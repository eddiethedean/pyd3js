from __future__ import annotations

import re
from pathlib import Path

import pyd3js_selection


def _read_upstream_exports() -> list[str]:
    md = (
        Path(__file__)
        .resolve()
        .parents[1]
        .joinpath("docs", "UPSTREAM_API.md")
        .read_text(encoding="utf-8")
    )
    names: list[str] = []
    for line in md.splitlines():
        m = re.match(r"^- `([^`]+)`\s*$", line)
        if m:
            names.append(m.group(1))
    assert names, "No upstream exports found in docs/UPSTREAM_API.md"
    return names


def _read_readme_matrix() -> dict[str, str]:
    md = (
        Path(__file__)
        .resolve()
        .parents[1]
        .joinpath("README.md")
        .read_text(encoding="utf-8")
    )
    out: dict[str, str] = {}
    for line in md.splitlines():
        m = re.match(r"^- `([^`]+)` — \[([^\]]+)\]\s*$", line)
        if not m:
            continue
        name, status = m.group(1), m.group(2)
        assert name not in out, (
            f"Duplicate entry in README compatibility matrix: {name}"
        )
        out[name] = status
    assert out, "No compatibility matrix entries found in README.md"
    return out


def test_readme_matrix_covers_all_upstream_exports() -> None:
    upstream = set(_read_upstream_exports())
    matrix = _read_readme_matrix()

    missing = sorted(upstream - set(matrix))
    extra = sorted(set(matrix) - upstream)
    assert missing == [], f"Missing from README compatibility matrix: {missing}"
    assert extra == [], f"Unexpected names in README compatibility matrix: {extra}"


def test_readme_matrix_matches_python_exports() -> None:
    matrix = _read_readme_matrix()
    exported = set(pyd3js_selection.__all__)

    exported_extras_allowed = {"__version__", "Selection", "document"}

    implemented: set[str] = set()
    for name, status in matrix.items():
        if status.startswith("missing"):
            continue
        implemented.add(name)

    missing_from_python = sorted(implemented - exported)
    assert missing_from_python == [], (
        "README marks implemented but not exported by pyd3js_selection: "
        f"{missing_from_python}"
    )

    upstream = set(_read_upstream_exports())
    unexpected_exports = sorted(exported - upstream - exported_extras_allowed)
    assert unexpected_exports == [], (
        f"Unexpected pyd3js_selection exports: {unexpected_exports}"
    )
