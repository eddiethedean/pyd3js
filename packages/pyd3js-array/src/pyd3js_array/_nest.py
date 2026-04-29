"""Internal helpers for D3-style nested map structures."""

from __future__ import annotations


class NestMap(dict):
    """Marker type for nested maps produced by group/index/rollup.

    This lets us distinguish map nodes from leaf values that may also be dicts.
    """
