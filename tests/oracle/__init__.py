"""Node+d3 oracle client (optional; requires `tools/oracle` npm install)."""

from tests.oracle.client import assert_approx_oracle, oracle_available, oracle_eval

__all__ = ["assert_approx_oracle", "oracle_available", "oracle_eval"]
