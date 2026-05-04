"""Shim for d3-geo `clip/buffer.js` — implementation in `clip._buffer`."""

from pyd3js_geo.clip._buffer import ClipBuffer, clip_buffer

__all__ = ["ClipBuffer", "clip_buffer"]
