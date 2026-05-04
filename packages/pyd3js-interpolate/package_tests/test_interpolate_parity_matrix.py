"""README compatibility matrix ↔ UPSTREAM_API ↔ exports (pyd3js-array pattern)."""

from __future__ import annotations

import re
from pathlib import Path

import pyd3js_interpolate as pi


def _read_upstream_exports() -> list[str]:
    md = (
        Path(__file__)
        .resolve()
        .parents[1]
        .joinpath("docs", "UPSTREAM_API.md")
        .read_text(encoding="utf-8")
    )
    names: list[str] = []
    in_exports = False
    for line in md.splitlines():
        if line.strip() == "## Exports (`src/index.js`)":
            in_exports = True
            continue
        if in_exports and line.startswith("## ") and "Exports" not in line:
            break
        if not in_exports:
            continue
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
    in_section = False
    for line in md.splitlines():
        if line.strip() == "### Upstream exports (`d3-interpolate@3.0.1`)":
            in_section = True
            continue
        if in_section and line.startswith("### "):
            break
        if not in_section:
            continue
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


def _allowed_python_extra(name: str) -> bool:
    if name == "__version__":
        return True
    if name in {"basis_fn", "generic_array", "is_number_array", "isNumberArray"}:
        return True
    if name.startswith("interpolate_"):
        return True
    return False


def test_readme_matrix_covers_all_upstream_exports() -> None:
    upstream = set(_read_upstream_exports())
    matrix = _read_readme_matrix()

    missing = sorted(upstream - set(matrix))
    extra = sorted(set(matrix) - upstream)
    assert missing == [], f"Missing from README compatibility matrix: {missing}"
    assert extra == [], f"Unexpected names in README compatibility matrix: {extra}"


def test_readme_matrix_matches_python_exports() -> None:
    matrix = _read_readme_matrix()
    exported = set(pi.__all__)
    upstream = set(_read_upstream_exports())

    implemented: set[str] = set()
    for name, status in matrix.items():
        if status.strip().lower().startswith("missing"):
            continue
        implemented.add(name)

    missing_from_python = sorted(implemented - exported)
    assert missing_from_python == [], (
        "README marks implemented but not exported by pyd3js_interpolate: "
        f"{missing_from_python}"
    )

    unexpected_exports = sorted(
        n for n in exported if n not in upstream and not _allowed_python_extra(n)
    )
    assert unexpected_exports == [], (
        f"Unexpected pyd3js_interpolate exports: {unexpected_exports}"
    )
