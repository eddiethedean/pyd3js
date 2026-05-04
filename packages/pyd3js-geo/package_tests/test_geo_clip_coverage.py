"""Direct tests for clip helpers to complete line coverage."""

from __future__ import annotations

from typing import Any


class _Pts:
    def __init__(self) -> None:
        self.points: list[tuple[float, float]] = []

    def point(self, x: float, y: float, z: Any = None) -> None:
        self.points.append((x, y))

    def lineStart(self) -> None:
        return None

    def lineEnd(self) -> None:
        return None


def test_clip_antimeridian_interpolate_branches() -> None:
    from pyd3js_geo.clip._antimeridian import (
        clip_antimeridian_interpolate,
        _clip_antimeridian_intersect,
    )

    s = _Pts()
    clip_antimeridian_interpolate(None, None, 1.0, s)
    assert len(s.points) >= 4

    s2 = _Pts()
    clip_antimeridian_interpolate([-2.5, 0.1], [2.5, 0.2], 1.0, s2)
    assert s2.points

    s3 = _Pts()
    clip_antimeridian_interpolate([0.1, 0.1], [0.2, 0.2], 1.0, s3)
    assert s3.points

    assert abs(_clip_antimeridian_intersect(0.0, 0.0, 0.0, 0.0) - 0.0) < 1e-9


def test_clip_antimeridian_line_crosses_antimeridian() -> None:
    from pyd3js_geo.clip._antimeridian import clip_antimeridian_line

    log: list[str] = []

    class S:
        def lineStart(self) -> None:
            log.append("ls")

        def lineEnd(self) -> None:
            log.append("le")

        def point(self, x: float, y: float, z: Any = None) -> None:
            log.append(f"p{x:.4f}")

    sink = S()
    h = clip_antimeridian_line(sink)
    h["lineStart"]()
    h["point"](2.5, 0.1)
    h["point"](-2.5, 0.2)
    h["lineEnd"]()
    assert "ls" in log


def test_clip_buffer_rejoin_noop() -> None:
    from pyd3js_geo.clip._buffer import ClipBuffer, noop as buf_noop

    buf_noop()
    b = ClipBuffer()
    b.lineStart()
    b.point(1.0, 2.0)
    b.lineEnd()
    b.rejoin()
    assert b.result()


def test_clip_line_rect_dy_negative_branch() -> None:
    from pyd3js_geo.clip._line import clip_line_rect

    assert clip_line_rect([0.0, 5.0], [10.0, -5.0], 0.0, -10.0, 20.0, 10.0) is True


def test_geo_clip_rectangle_and_extent_edges() -> None:
    from pyd3js_geo import geoClipCircle, geoClipRectangle

    class S:
        def lineStart(self) -> None:
            return None

        def lineEnd(self) -> None:
            return None

        def point(self, *_a: Any, **_k: Any) -> None:
            return None

    geoClipCircle(1.7)(S())
    geoClipRectangle(0.0, 0.0, 100.0, 100.0)(S())


def test_geo_graticule10_invocation() -> None:
    from pyd3js_geo import geoGraticule10

    g = geoGraticule10()
    assert g["type"] == "MultiLineString"


def test_wrap_mercator_center_setter_and_resample_sphere() -> None:
    from pyd3js_geo import geoMercator, geoTransverseMercator
    from pyd3js_geo._resample import _Resample, _ResampleNone

    m = geoMercator()
    m.center([12.0, 34.0])

    tm = geoTransverseMercator()
    tm.center([-5.0, 10.0])

    class Inner:
        pass

    _ResampleNone(lambda la, ph: [la, ph], Inner()).sphere()
    _Resample(lambda la, ph: [la, ph], 0.01, Inner()).sphere()


def test_conic_conformal_raw_returns_mercator_when_n_zero() -> None:
    from pyd3js_geo._projection_geo import conicConformalRaw, mercatorRaw

    assert conicConformalRaw(0.0, 0.0) is mercatorRaw
