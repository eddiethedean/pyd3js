from __future__ import annotations

from collections.abc import Generator

import pytest

from pyd3js_timer._engine import _reset_for_tests, _set_wall_ms_factory


@pytest.fixture(autouse=True)
def _isolate_timer_module() -> Generator[None, None, None]:
    _reset_for_tests()
    _set_wall_ms_factory(None)
    yield
    _reset_for_tests()
    _set_wall_ms_factory(None)
