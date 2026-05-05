"""Gate: public exports stay aligned with documented upstream surface."""

from __future__ import annotations

import pyd3js_transition


def test_package_all_matches_upstream_inventory() -> None:
    # UPSTREAM_API.md — entry exports + transition submodule (Python exposes superset).
    expected = {
        "Transition",
        "__version__",
        "active",
        "interrupt",
        "new_id",
        "transition",
    }
    assert set(pyd3js_transition.__all__) == expected


def test_upstream_entry_exports_are_importable() -> None:
    from pyd3js_transition import active, interrupt, transition

    assert callable(transition)
    assert callable(active)
    assert callable(interrupt)


def test_transition_submodule_exports_are_importable() -> None:
    from pyd3js_transition import Transition, new_id

    assert isinstance(Transition, type)
    tid = new_id()
    assert isinstance(tid, int)
    assert new_id() != tid
