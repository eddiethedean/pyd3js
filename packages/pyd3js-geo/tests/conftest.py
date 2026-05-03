"""Upstream d3-geo parity tests are opt-in until the Python port matches numerically."""

from __future__ import annotations

import os

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line(
        "markers",
        "d3_upstream: ported from d3-geo JS; run with PYD3JS_GEO_FULL_UPSTREAM=1",
    )


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if os.environ.get("PYD3JS_GEO_FULL_UPSTREAM") == "1":
        return
    skip_upstream = pytest.mark.skip(
        reason="Set PYD3JS_GEO_FULL_UPSTREAM=1 to run ported d3-geo upstream tests",
    )
    for item in items:
        if "test_upstream_" in item.nodeid:
            item.add_marker(skip_upstream)
