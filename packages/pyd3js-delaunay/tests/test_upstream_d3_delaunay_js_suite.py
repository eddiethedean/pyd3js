from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest


@pytest.mark.upstream
def test_upstream_d3_delaunay_mocha_suite_passes() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    upstream = repo_root / "packages" / "pyd3js-delaunay" / "upstream" / "d3-delaunay"
    if not upstream.is_dir():
        pytest.skip(
            "Upstream d3-delaunay repo not vendored (run scripts/vendor_upstream.py)."
        )

    node_modules = upstream / "node_modules"
    if not node_modules.is_dir():
        pytest.skip(
            "Upstream d3-delaunay node_modules not installed. Run: "
            "`cd packages/pyd3js-delaunay/upstream/d3-delaunay && npm install`"
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
            "Upstream d3-delaunay mocha suite failed.\n\n"
            f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
        )
