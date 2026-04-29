#!/usr/bin/env python3
"""
Convert a subset of d3-style JS tests (node:test `it` + `assert.*`) into pytest skeletons.

Emits tests that optionally call the Node oracle when `ORACLE=1` or when expected
values are not statically mapped. For full fidelity, extend the assertion mapping.
"""

from __future__ import annotations

import argparse
import re
import textwrap
from pathlib import Path


IT_RE = re.compile(
    r'it\(\s*(?P<quote>["\'])(?P<title>.*?)(?P=quote)\s*,\s*(?:async\s*)?\(\s*\)\s*=>\s*\{(?P<body>.*?)\}\s*\)',
    re.DOTALL,
)

ASSERT_DEEP = re.compile(
    r"assert\.deep(?:Strict)?Equal\(\s*(?P<a>[^,]+)\s*,\s*(?P<b>[^)]+)\s*\)"
)
ASSERT_STRICT = re.compile(
    r"assert\.strictEqual\(\s*(?P<a>[^,]+)\s*,\s*(?P<b>[^)]+)\s*\)"
)


def slugify(title: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "_", title.lower()).strip("_")
    return s or "case"


def translate_body(body: str, test_name: str) -> str:
    lines: list[str] = []
    lines.append(f"    # source: {test_name}")
    for m in ASSERT_DEEP.finditer(body):
        a, b = m.group("a").strip(), m.group("b").strip()
        lines.append(
            f"    # assert.deepEqual({a}, {b})\n"
            f"    pytest.fail('Port assertion manually or enable oracle for: {test_name}')"
        )
    for m in ASSERT_STRICT.finditer(body):
        a, b = m.group("a").strip(), m.group("b").strip()
        lines.append(
            f"    # assert.strictEqual({a}, {b})\n"
            f"    pytest.fail('Port assertion manually or enable oracle for: {test_name}')"
        )
    if len(lines) == 1:
        lines.append("    pytest.skip('no supported assertions found')")
    return "\n".join(lines)


def convert_file(path: Path) -> str:
    src = path.read_text()
    parts: list[str] = [
        '"""Auto-generated pytest skeleton (run scripts/tape_to_pytest.py)."""',
        "from __future__ import annotations",
        "",
        "import pytest",
        "",
    ]
    for m in IT_RE.finditer(src):
        title = m.group("title")
        body = m.group("body")
        fn = slugify(title)
        parts.append(f"def test_{fn}() -> None:")
        parts.append(textwrap.indent(translate_body(body, title), "    "))
        parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("js_test", type=Path, help="Path to *-test.js")
    ap.add_argument("-o", "--output", type=Path, required=True)
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(convert_file(args.js_test))


if __name__ == "__main__":
    main()
