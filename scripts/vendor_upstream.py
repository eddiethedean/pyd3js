#!/usr/bin/env python3
"""Clone upstream d3-* repos into packages/pyd3js-<name>/upstream/<repo> at pinned tags."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "upstream_lock.json"
PACKAGES = ROOT / "packages"


def main() -> None:
    locks = json.loads(LOCK.read_text())
    for npm_name, version in sorted(locks.items()):
        if npm_name == "d3":
            repo = "https://github.com/d3/d3.git"
            tag = f"v{version}"
            dest = ROOT / "upstream" / "d3"
        else:
            repo = f"https://github.com/d3/{npm_name}.git"
            tag = f"v{version}"
            slug = npm_name.replace("d3-", "pyd3js-")
            dest = PACKAGES / slug / "upstream" / npm_name

        dest.parent.mkdir(parents=True, exist_ok=True)
        if (dest / ".git").exists():
            print(f"skip existing {dest}")
            continue
        print(f"cloning {repo} @ {tag} -> {dest}")
        subprocess.run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                tag,
                repo,
                str(dest),
            ],
            check=True,
        )


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
