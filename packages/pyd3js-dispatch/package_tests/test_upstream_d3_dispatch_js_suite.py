from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

import pytest


@pytest.mark.upstream
def test_upstream_d3_dispatch_mocha_suite_passes() -> None:
    """Run the upstream `d3-dispatch` JS test suite (vendored) and assert it passes."""

    repo_root = Path(__file__).resolve().parents[3]
    upstream = repo_root / "packages" / "pyd3js-dispatch" / "upstream" / "d3-dispatch"
    if not upstream.is_dir():
        pytest.skip(
            "Upstream d3-dispatch repo not vendored (run scripts/vendor_upstream.py)."
        )

    # Avoid doing installs during pytest; require that node_modules is already present.
    node_modules = upstream / "node_modules"
    if not node_modules.is_dir():
        pytest.skip(
            "Upstream d3-dispatch node_modules not installed. Run: "
            "`cd packages/pyd3js-dispatch/upstream/d3-dispatch && npm install`"
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
            "Upstream d3-dispatch mocha suite failed.\n\n"
            f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
        )
