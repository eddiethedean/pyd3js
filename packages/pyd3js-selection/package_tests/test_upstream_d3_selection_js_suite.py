from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest


@pytest.mark.upstream
def test_upstream_d3_selection_mocha_suite_passes() -> None:
    """Run the vendored upstream `d3-selection` JS test suite (Mocha) and assert it passes."""

    repo_root = Path(__file__).resolve().parents[3]
    upstream = repo_root / "packages" / "pyd3js-selection" / "upstream" / "d3-selection"
    if not upstream.is_dir():
        pytest.skip("Upstream d3-selection repo not vendored (run scripts/vendor_upstream.py).")

    node_modules = upstream / "node_modules"
    if not node_modules.is_dir():
        pytest.skip(
            "Upstream d3-selection node_modules not installed. Run: "
            "`cd packages/pyd3js-selection/upstream/d3-selection && npm install --legacy-peer-deps`"
        )

    env = os.environ.copy()
    env.setdefault("NPM_CONFIG_FUND", "false")
    env.setdefault("NPM_CONFIG_AUDIT", "false")

    def _run() -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["npm", "test"],
            cwd=str(upstream),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    proc = _run()
    if proc.returncode != 0 and "spawn sh EAGAIN" in (proc.stderr or ""):
        time.sleep(1.0)
        proc = _run()
    if proc.returncode != 0:
        raise AssertionError(
            "Upstream d3-selection mocha suite failed.\n\n"
            f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
        )

