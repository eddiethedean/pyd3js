from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.mark.upstream
def test_upstream_d3_drag_mocha_suite_passes() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    upstream = repo_root / "packages" / "pyd3js-drag" / "upstream" / "d3-drag"
    if not upstream.is_dir():
        pytest.skip(
            "Upstream d3-drag repo not vendored (run scripts/vendor_upstream.py)."
        )

    node_modules = upstream / "node_modules"
    if not node_modules.is_dir():
        pytest.skip(
            "Upstream d3-drag node_modules missing; run "
            "`cd packages/pyd3js-drag/upstream/d3-drag && npm install --legacy-peer-deps`"
        )

    proc = subprocess.run(
        ["npm", "test"],
        cwd=str(upstream),
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(
            "Upstream d3-drag mocha suite failed.\n\n"
            f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
        )
