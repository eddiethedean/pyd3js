import pytest


@pytest.mark.skip(reason="internal polygonContains not exported")
def test_upstream_polygon_contains_not_ported():
    """Upstream polygonContains-test.js targets an internal module."""
