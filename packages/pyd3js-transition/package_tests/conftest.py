from __future__ import annotations

from collections.abc import Generator

import pytest


@pytest.fixture(autouse=True)
def _reset_selection_patches() -> Generator[None, None, None]:
    # Ensure pyd3js_transition import side-effect has run for every test module.
    import pyd3js_transition  # noqa: F401

    import pyd3js_timer._engine as timer_engine

    timer_engine._reset_for_tests()
    yield
    timer_engine._reset_for_tests()

