"""geoTransform factory (d3-geo `transform.js`)."""

from __future__ import annotations

from typing import Any, Callable

from pyd3js_geo.stream import TransformStream, transformer


class _GeoTransform:
    def __init__(self, methods: dict[str, Callable[..., Any]]):
        self._methods = methods

    def stream(self, stream: Any) -> TransformStream:
        return transformer(self._methods)(stream)


def geoTransform(methods: dict[str, Callable[..., Any]]) -> _GeoTransform:
    return _GeoTransform(methods)
