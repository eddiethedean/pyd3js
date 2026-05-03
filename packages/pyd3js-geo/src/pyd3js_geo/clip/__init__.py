"""Spherical / planar clipping streams (d3-geo `clip/*`)."""

from pyd3js_geo.clip._antimeridian import clip_antimeridian
from pyd3js_geo.clip._circle import clip_circle
from pyd3js_geo.clip._rectangle import clip_rectangle

__all__ = ["clip_antimeridian", "clip_circle", "clip_rectangle"]
