from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.upstream
def test_upstream_d3_array_mocha_suite_passes() -> None:
    """Run the upstream `d3-array` JS test suite (vendored) and assert it passes.

    This is the most direct way to ensure we have incorporated the full upstream test
    suite for the pinned version.
    """

    repo_root = Path(__file__).resolve().parents[3]
    upstream = repo_root / "packages" / "pyd3js-array" / "upstream" / "d3-array"
    if not upstream.is_dir():
        pytest.skip("Upstream d3-array repo not vendored (run scripts/vendor_upstream.py).")

    # Avoid doing installs during pytest; require that node_modules is already present.
    node_modules = upstream / "node_modules"
    if not node_modules.is_dir():
        pytest.skip(
            "Upstream d3-array node_modules not installed. Run: "
            "`cd packages/pyd3js-array/upstream/d3-array && npm install`"
        )

    env = os.environ.copy()
    # Keep npm quieter in CI output.
    env.setdefault("NPM_CONFIG_FUND", "false")
    env.setdefault("NPM_CONFIG_AUDIT", "false")

    proc = subprocess.run(
        ["npm", "test"],
        cwd=str(upstream),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise AssertionError(
            "Upstream d3-array mocha suite failed.\n\n"
            f"stdout:\n{proc.stdout}\n\nstderr:\n{proc.stderr}"
        )

