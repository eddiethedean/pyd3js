from __future__ import annotations

import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Example:
    code: str
    expected_stdout: str
    source: Path


def _extract_examples(md: str, source: Path) -> list[Example]:
    lines = md.splitlines()
    i = 0
    blocks: list[tuple[str, str]] = []
    while i < len(lines):
        m = re.match(r"^```([a-zA-Z0-9_-]+)\s*$", lines[i])
        if not m:
            i += 1
            continue
        lang = m.group(1).strip()
        i += 1
        body_lines: list[str] = []
        while i < len(lines) and lines[i] != "```":
            body_lines.append(lines[i])
            i += 1
        # skip closing fence
        if i < len(lines) and lines[i] == "```":
            i += 1
        blocks.append((lang, "\n".join(body_lines).rstrip() + "\n"))

    out: list[Example] = []
    for (lang, body), (next_lang, next_body) in zip(blocks, blocks[1:]):
        if lang == "python" and next_lang == "text":
            out.append(Example(code=body, expected_stdout=next_body, source=source))
    return out


def _run_python(code: str) -> str:
    proc = subprocess.run(
        [sys.executable, "-c", code],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout.replace("\r\n", "\n")


def test_markdown_examples_match_real_output() -> None:
    root = Path(__file__).resolve().parents[1]
    md_files = [
        root / "README.md",
        root / "docs" / "USER_GUIDE.md",
    ]

    examples: list[Example] = []
    for p in md_files:
        examples.extend(_extract_examples(p.read_text(encoding="utf-8"), p))

    assert examples, "No python/text example pairs found"

    for ex in examples:
        got = _run_python(ex.code)
        exp = ex.expected_stdout.replace("\r\n", "\n")
        assert got == exp, f"Mismatch in {ex.source}"

