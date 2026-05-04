from __future__ import annotations

import pytest

import pyd3js_selection._globals as g
from pyd3js_selection._dom import parse_html


@pytest.fixture
def jsdom():
    """Tiny jsdom-like fixture: sets global document/window for tests."""

    def _set(html: str = ""):
        doc = parse_html(html)
        g.document = doc
        return doc

    try:
        yield _set
    finally:
        g.document = None
