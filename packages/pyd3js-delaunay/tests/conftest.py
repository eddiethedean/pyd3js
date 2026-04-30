from __future__ import annotations

import pytest


@pytest.fixture
def require_node_mesh() -> None:
    """Reserved for tests that historically gated on the Node delaunator bridge (removed)."""
    return None
