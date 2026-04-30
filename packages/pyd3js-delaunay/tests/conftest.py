from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def require_node_mesh() -> None:
    from pyd3js_delaunay._delaunator import _mesh_script

    script = _mesh_script()
    bundled = (
        Path(__file__).resolve().parents[3]
        / "tools"
        / "oracle"
        / "node_modules"
        / "delaunator"
        / "index.js"
    )
    if not script.is_file() or not bundled.is_file():
        pytest.skip("Delaunator mesh requires tools/oracle with npm install (delaunator).")
