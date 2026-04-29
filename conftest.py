from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "oracle: requires Node oracle (tools/oracle npm install)")


@pytest.fixture
def require_oracle() -> None:
    from tests.oracle.client import oracle_available

    if not oracle_available():
        pytest.skip("Oracle unavailable: run npm install in tools/oracle")
