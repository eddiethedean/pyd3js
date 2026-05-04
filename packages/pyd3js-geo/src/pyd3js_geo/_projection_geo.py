from __future__ import annotations

import math
from typing import Any, Callable

from pyd3js_geo._albers_usa import geo_albers_usa
from pyd3js_geo._bounds_geo import geo_bounds_from_stream
from pyd3js_geo._centroid_geo import geo_centroid_from_stream
from pyd3js_geo._geo_area_stream import geo_area_from_stream
from pyd3js_geo._graticule_geo import geo_graticule_factory
from pyd3js_geo._identity_proj import geo_identity
from pyd3js_geo._mercator_geo import wrap_mercator_projection
from pyd3js_geo._fit import fitExtent, fitHeight, fitSize, fitWidth
from pyd3js_geo._resample import resample_factory
from pyd3js_geo.clip._antimeridian import clip_antimeridian
from pyd3js_geo.clip._circle import clip_circle
from pyd3js_geo.clip._rectangle import clip_rectangle
from pyd3js_geo.compose import geo_compose_project
from pyd3js_geo.identity import identity
from pyd3js_geo.math import (
    acos,
    asin,
    degrees,
    ecma_mod,
    epsilon,
    epsilon2,
    halfPi,
    pi,
    radians,
    sign,
    tau,
)
from pyd3js_geo.rotation import geoRotation, rotateRadians
from pyd3js_geo.stream import (
    TransformStream,
    _transform_radians_factory,
    _transform_rotate_factory,
    geoStream,
    transformer,
)
from pyd3js_geo.transform import _GeoTransform, geoTransform

_MISSING = object()


def _scale_translate_rotate(
    k: float, dx: float, dy: float, sx: float, sy: float, alpha: float
) -> Callable[[float, float], list[float]]:
    if not alpha:

        def transform(x: float, y: float) -> list[float]:
            x *= sx
            y *= sy
            return [dx + k * x, dy - k * y]

        transform.invert = lambda x, y: [(x - dx) / k * sx, (dy - y) / k * sy]  # type: ignore[attr-defined]
        return transform
    ca, sa = math.cos(alpha), math.sin(alpha)
    a, b = ca * k, sa * k
    ai, bi = ca / k, sa / k
    ci, fi = (sa * dy - ca * dx) / k, (sa * dx + ca * dy) / k

    def transform(x: float, y: float) -> list[float]:
        x *= sx
        y *= sy
        return [a * x - b * y + dx, dy - b * x - a * y]

    transform.invert = lambda x, y: [
        sx * (ai * x - bi * y + ci),
        sy * (fi - bi * x - ai * y),
    ]  # type: ignore[attr-defined]
    return transform


class Projection:
    def __init__(self, raw: Callable[[float, float], list[float]]):
        self._raw = raw
        self._k, self._x, self._y = 150.0, 480.0, 250.0
        self._lambda = self._phi = self._delta_lambda = self._delta_phi = (
            self._delta_gamma
        ) = self._alpha = 0.0
        self._sx = self._sy = 1.0
        self._theta: float | None = None
        self._clip_extent = None
        self._delta2 = 0.5
        self._preclip: Any = clip_antimeridian
        self._postclip: Any = identity
        self._stream_cache: Any = None
        self._stream_cache_stream: Any = None
        self._recenter()

    def _reset_stream_cache(self) -> None:
        self._stream_cache = None
        self._stream_cache_stream = None

    def _recenter(self) -> "Projection":
        center = _scale_translate_rotate(
            self._k, 0, 0, self._sx, self._sy, self._alpha
        )(*self._raw(self._lambda, self._phi))
        self._transform = _scale_translate_rotate(
            self._k,
            self._x - center[0],
            self._y - center[1],
            self._sx,
            self._sy,
            self._alpha,
        )
        self._rotate = rotateRadians(
            self._delta_lambda, self._delta_phi, self._delta_gamma
        )
        self._project_transform = geo_compose_project(self._raw, self._transform)
        self._project_rotate_transform = geo_compose_project(
            self._rotate, self._project_transform
        )
        self._project_resample_factory = resample_factory(
            self._project_transform, self._delta2
        )
        self._reset_stream_cache()
        return self

    def __call__(self, point: list[float] | tuple[float, float]) -> list[float]:
        return self._project_rotate_transform(point[0] * radians, point[1] * radians)

    def invert(self, point: list[float] | tuple[float, float]) -> list[float] | None:
        if not hasattr(self._raw, "invert"):
            return None
        p = self._project_rotate_transform.invert(point[0], point[1])  # type: ignore[attr-defined]
        if p is None:
            return None
        return [p[0] * degrees, p[1] * degrees]

    def stream(self, stream: Any) -> Any:
        if self._stream_cache is not None and self._stream_cache_stream is stream:
            return self._stream_cache
        self._stream_cache_stream = stream
        s = self._postclip(stream)
        s = self._project_resample_factory(s)
        s = self._preclip(s)
        s = _transform_rotate_factory(self._rotate)(s)
        self._stream_cache = _transform_radians_factory()(s)
        return self._stream_cache

    def preclip(self, value: Any = _MISSING):
        if value is _MISSING:
            return self._preclip
        self._preclip = value
        self._theta = None
        self._reset_stream_cache()
        return self

    def postclip(self, value: Any = _MISSING):
        if value is _MISSING:
            return self._postclip
        self._postclip = value
        self._clip_extent = None
        self._reset_stream_cache()
        return self

    def clipAngle(self, value: Any = _MISSING):
        if value is _MISSING:
            return None if self._theta is None else self._theta * degrees
        self._theta = float(value) * radians if value else None
        self._preclip = (
            clip_circle(self._theta) if self._theta is not None else clip_antimeridian
        )
        self._reset_stream_cache()
        return self

    def clipExtent(self, value: Any = _MISSING):
        if value is _MISSING:
            return self._clip_extent
        if value is None:
            self._clip_extent = None
            self._postclip = identity
        else:
            self._clip_extent = [
                [float(value[0][0]), float(value[0][1])],
                [float(value[1][0]), float(value[1][1])],
            ]
            self._postclip = clip_rectangle(
                float(value[0][0]),
                float(value[0][1]),
                float(value[1][0]),
                float(value[1][1]),
            )
        self._reset_stream_cache()
        return self

    def scale(self, value: Any = _MISSING):
        if value is _MISSING:
            return self._k
        self._k = float(value)
        return self._recenter()

    def translate(self, value: Any = _MISSING):
        if value is _MISSING:
            return [self._x, self._y]
        self._x, self._y = float(value[0]), float(value[1])
        return self._recenter()

    def center(self, value: Any = _MISSING):
        if value is _MISSING:
            return [self._lambda * degrees, self._phi * degrees]
        self._lambda, self._phi = (
            ecma_mod(float(value[0])) * radians,
            ecma_mod(float(value[1])) * radians,
        )
        return self._recenter()

    def rotate(self, value: Any = _MISSING):
        if value is _MISSING:
            return [
                self._delta_lambda * degrees,
                self._delta_phi * degrees,
                self._delta_gamma * degrees,
            ]
        self._delta_lambda, self._delta_phi = (
            ecma_mod(float(value[0])) * radians,
            ecma_mod(float(value[1])) * radians,
        )
        self._delta_gamma = ecma_mod(float(value[2])) * radians if len(value) > 2 else 0
        return self._recenter()

    def angle(self, value: Any = _MISSING):
        if value is _MISSING:
            return self._alpha * degrees
        self._alpha = ecma_mod(float(value)) * radians
        return self._recenter()

    def reflectX(self, value: Any = _MISSING):
        if value is _MISSING:
            return self._sx < 0
        self._sx = -1 if value else 1
        return self._recenter()

    def reflectY(self, value: Any = _MISSING):
        if value is _MISSING:
            return self._sy < 0
        self._sy = -1 if value else 1
        return self._recenter()

    def precision(self, value: Any = _MISSING):
        if value is _MISSING:
            return math.sqrt(self._delta2)
        v = float(value)
        self._delta2 = v * v
        self._project_resample_factory = resample_factory(
            self._project_transform, self._delta2
        )
        self._reset_stream_cache()
        return self

    def fitExtent(self, extent: list[list[float]], obj: Any):
        return fitExtent(self, extent, obj)

    def fitSize(self, size: list[float], obj: Any):
        return fitSize(self, size, obj)

    def fitWidth(self, width: float, obj: Any):
        return fitWidth(self, width, obj)

    def fitHeight(self, height: float, obj: Any):
        return fitHeight(self, height, obj)


def geoProjection(raw: Callable[[float, float], list[float]]) -> Projection:
    return Projection(raw)


def geoProjectionMutator(
    project_at: Callable[..., Callable[[float, float], list[float]]],
):
    return lambda *args: Projection(project_at(*args))


def geoIdentity() -> Any:
    return geo_identity()


def equirectangularRaw(lambda_: float, phi: float) -> list[float]:
    return [lambda_, phi]


equirectangularRaw.invert = equirectangularRaw  # type: ignore[attr-defined]


def geoEquirectangular() -> Projection:
    return geoProjection(equirectangularRaw).scale(152.63)


def mercatorRaw(lambda_: float, phi: float) -> list[float]:
    t = math.tan((halfPi + phi) / 2)
    if t <= 0 or math.isnan(t):
        y = float("-inf")
    else:
        y = math.log(t)
    return [lambda_, y]


def _mercator_invert(x: float, y: float) -> list[float]:
    if y == float("-inf"):
        return [x, -halfPi]
    if y == float("inf"):
        return [x, halfPi]
    return [x, 2 * math.atan(math.exp(y)) - halfPi]


mercatorRaw.invert = _mercator_invert  # type: ignore[attr-defined]


def geoMercator() -> Projection:
    m = geoProjection(mercatorRaw).scale(961 / tau)
    return wrap_mercator_projection(m, True)


def transverseMercatorRaw(lambda_: float, phi: float) -> list[float]:
    t = math.tan((halfPi + phi) / 2)
    if t <= 0 or math.isnan(t):
        x = float("-inf")
    else:
        x = math.log(t)
    return [x, -lambda_]


def _transverse_mercator_invert(x: float, y: float) -> list[float]:
    if x == float("-inf"):
        phi = -halfPi
    elif x == float("inf"):
        phi = halfPi
    else:
        phi = 2 * math.atan(math.exp(x)) - halfPi
    return [-y, phi]


transverseMercatorRaw.invert = _transverse_mercator_invert  # type: ignore[attr-defined]


def geoTransverseMercator() -> Projection:
    m = geoProjection(transverseMercatorRaw).rotate([0, 0, 90]).scale(159.155)
    return wrap_mercator_projection(m, False)


def azimuthalRaw(
    scale: Callable[[float], float],
) -> Callable[[float, float], list[float]]:
    def raw(x: float, y: float) -> list[float]:
        cx, cy = math.cos(x), math.cos(y)
        k = scale(cx * cy)
        return [2, 0] if k == math.inf else [k * cy * math.sin(x), k * math.sin(y)]

    return raw


def azimuthalInvert(
    angle: Callable[[float], float],
) -> Callable[[float, float], list[float]]:
    def invert(x: float, y: float) -> list[float]:
        z = math.sqrt(x * x + y * y)
        c = angle(z)
        return [
            math.atan2(x * math.sin(c), z * math.cos(c)),
            asin(y * math.sin(c) / z if z else 0),
        ]

    return invert


azimuthalEqualAreaRaw = azimuthalRaw(lambda c: math.sqrt(2 / max(1 + c, epsilon2)))
azimuthalEqualAreaRaw.invert = azimuthalInvert(lambda z: 2 * asin(z / 2))  # type: ignore[attr-defined]
azimuthalEquidistantRaw = azimuthalRaw(
    lambda c: (lambda a: a / math.sin(a) if a else 0)(
        acos(max(-1 + epsilon2, min(1 - epsilon2, c)))
    )
)
azimuthalEquidistantRaw.invert = azimuthalInvert(lambda z: z)  # type: ignore[attr-defined]


def gnomonicRaw(x: float, y: float) -> list[float]:
    cy = math.cos(y)
    k = math.cos(x) * cy
    return [cy * math.sin(x) / k, math.sin(y) / k]


gnomonicRaw.invert = azimuthalInvert(math.atan)  # type: ignore[attr-defined]


def orthographicRaw(x: float, y: float) -> list[float]:
    return [math.cos(y) * math.sin(x), math.sin(y)]


orthographicRaw.invert = azimuthalInvert(asin)  # type: ignore[attr-defined]


def stereographicRaw(x: float, y: float) -> list[float]:
    cy = math.cos(y)
    k = 1 + math.cos(x) * cy
    return [cy * math.sin(x) / k, math.sin(y) / k]


stereographicRaw.invert = azimuthalInvert(lambda z: 2 * math.atan(z))  # type: ignore[attr-defined]


def geoAzimuthalEqualArea() -> Projection:
    return geoProjection(azimuthalEqualAreaRaw).scale(124.75).clipAngle(180 - 1e-3)


def geoAzimuthalEquidistant() -> Projection:
    return geoProjection(azimuthalEquidistantRaw).scale(79.4188).clipAngle(180 - 1e-3)


def geoGnomonic() -> Projection:
    return geoProjection(gnomonicRaw).scale(144.049).clipAngle(60)


def geoOrthographic() -> Projection:
    return geoProjection(orthographicRaw).scale(249.5).clipAngle(90 + epsilon)


def geoStereographic() -> Projection:
    return geoProjection(stereographicRaw).scale(250).clipAngle(142)


def naturalEarth1Raw(lambda_: float, phi: float) -> list[float]:
    p2, p4 = phi * phi, phi * phi * phi * phi
    return [
        lambda_
        * (
            0.8707
            - 0.131979 * p2
            + p4 * (-0.013791 + p4 * (0.003971 * p2 - 0.001529 * p4))
        ),
        phi
        * (
            1.007226
            + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4))
        ),
    ]


def _natural_invert(x: float, y: float) -> list[float]:
    phi = y
    for _ in range(25):
        p2, p4 = phi * phi, phi * phi * phi * phi
        delta = (
            phi
            * (
                1.007226
                + p2 * (0.015085 + p4 * (-0.044475 + 0.028874 * p2 - 0.005916 * p4))
            )
            - y
        ) / (
            1.007226
            + p2
            * (
                0.015085 * 3
                + p4 * (-0.044475 * 7 + 0.028874 * 9 * p2 - 0.005916 * 11 * p4)
            )
        )
        phi -= delta
        if abs(delta) <= epsilon:
            break
    p2 = phi * phi
    return [
        x
        / (
            0.8707
            + p2
            * (-0.131979 + p2 * (-0.013791 + p2 * p2 * p2 * (0.003971 - 0.001529 * p2)))
        ),
        phi,
    ]


naturalEarth1Raw.invert = _natural_invert  # type: ignore[attr-defined]

A1, A2, A3, A4, M = 1.340264, -0.081106, 0.000893, 0.003796, math.sqrt(3) / 2


def equalEarthRaw(lambda_: float, phi: float) -> list[float]:
    l = asin(M * math.sin(phi))
    l2 = l * l
    l6 = l2 * l2 * l2
    return [
        lambda_ * math.cos(l) / (M * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2))),
        l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2)),
    ]


def _equal_invert(x: float, y: float) -> list[float]:
    l = y
    l2 = l * l
    l6 = l2 * l2 * l2
    for _ in range(12):
        delta = (l * (A1 + A2 * l2 + l6 * (A3 + A4 * l2)) - y) / (
            A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)
        )
        l -= delta
        l2 = l * l
        l6 = l2 * l2 * l2
        if abs(delta) < epsilon2:
            break
    return [
        M * x * (A1 + 3 * A2 * l2 + l6 * (7 * A3 + 9 * A4 * l2)) / math.cos(l),
        asin(math.sin(l) / M),
    ]


equalEarthRaw.invert = _equal_invert  # type: ignore[attr-defined]


def geoNaturalEarth1() -> Projection:
    return geoProjection(naturalEarth1Raw).scale(175.295)


def geoEqualEarth() -> Projection:
    return geoProjection(equalEarthRaw).scale(177.158)


def cylindricalEqualAreaRaw(phi0: float):
    cp0 = math.cos(phi0)

    def raw(lambda_: float, phi: float) -> list[float]:
        return [lambda_ * cp0, math.sin(phi) / cp0]

    raw.invert = lambda x, y: [x / cp0, asin(y * cp0)]  # type: ignore[attr-defined]
    return raw


def conicEqualAreaRaw(y0: float, y1: float):
    sy0 = math.sin(y0)
    n = (sy0 + math.sin(y1)) / 2
    if abs(n) < epsilon:
        return cylindricalEqualAreaRaw(y0)
    c = 1 + sy0 * (2 * n - sy0)
    r0 = math.sqrt(c) / n

    def raw(x: float, y: float) -> list[float]:
        r = math.sqrt(c - 2 * n * math.sin(y)) / n
        return [r * math.sin(x * n), r0 - r * math.cos(x * n)]

    def inv(x: float, y: float) -> list[float]:
        r0y = r0 - y
        l = math.atan2(x, abs(r0y)) * sign(r0y)
        if r0y * n < 0:
            l -= pi * sign(x) * sign(r0y)
        return [l / n, asin((c - (x * x + r0y * r0y) * n * n) / (2 * n))]

    raw.invert = inv  # type: ignore[attr-defined]
    return raw


def conicConformalRaw(y0: float, y1: float):
    tany = lambda y: math.tan((halfPi + y) / 2)
    cy0 = math.cos(y0)
    n = (
        math.sin(y0)
        if y0 == y1
        else math.log(cy0 / math.cos(y1)) / math.log(tany(y1) / tany(y0))
    )
    if not n:
        return mercatorRaw
    f = cy0 * (tany(y0) ** n) / n

    def raw(x: float, y: float) -> list[float]:
        y = max(y, -halfPi + epsilon) if f > 0 else min(y, halfPi - epsilon)
        r = f / (tany(y) ** n)
        return [r * math.sin(n * x), f - r * math.cos(n * x)]

    raw.invert = lambda x, y: [
        math.atan2(x, abs(f - y)) * sign(f - y) / n,
        2 * math.atan((f / (sign(n) * math.sqrt(x * x + (f - y) * (f - y)))) ** (1 / n))
        - halfPi,
    ]  # type: ignore[attr-defined]
    return raw


def conicEquidistantRaw(y0: float, y1: float):
    cy0 = math.cos(y0)
    n = math.sin(y0) if y0 == y1 else (cy0 - math.cos(y1)) / (y1 - y0)
    if abs(n) < epsilon:
        return equirectangularRaw
    g = cy0 / n + y0

    def raw(x: float, y: float) -> list[float]:
        gy = g - y
        nx = n * x
        return [gy * math.sin(nx), g - gy * math.cos(nx)]

    raw.invert = lambda x, y: [
        math.atan2(x, abs(g - y)) * sign(g - y) / n,
        g - sign(n) * math.sqrt(x * x + (g - y) * (g - y)),
    ]  # type: ignore[attr-defined]
    return raw


class ConicProjection(Projection):
    def __init__(
        self,
        project_at: Callable[[float, float], Callable[[float, float], list[float]]],
        phi0: float = 0,
        phi1: float = pi / 3,
    ):
        self._project_at, self._phi0, self._phi1 = project_at, phi0, phi1
        super().__init__(project_at(phi0, phi1))

    def parallels(self, value: Any = _MISSING):
        if value is _MISSING:
            return [self._phi0 * degrees, self._phi1 * degrees]
        self._phi0, self._phi1 = float(value[0]) * radians, float(value[1]) * radians
        self._raw = self._project_at(self._phi0, self._phi1)
        return self._recenter()


def geoConicConformal() -> ConicProjection:
    return ConicProjection(conicConformalRaw).scale(109.5).parallels([30, 30])


def geoConicEqualArea() -> ConicProjection:
    return ConicProjection(conicEqualAreaRaw).scale(155.424).center([0, 33.6442])


def geoConicEquidistant() -> ConicProjection:
    return ConicProjection(conicEquidistantRaw).scale(131.154).center([0, 13.9389])


def geoAlbers() -> ConicProjection:
    return (
        geoConicEqualArea()
        .parallels([29.5, 45.5])
        .scale(1070)
        .translate([480, 250])
        .rotate([96, 0])
        .center([-0.6, 38.7])
    )


def geoAlbersUsa() -> Any:
    return geo_albers_usa()


geoAzimuthalEqualAreaRaw = azimuthalEqualAreaRaw
geoAzimuthalEquidistantRaw = azimuthalEquidistantRaw
geoConicConformalRaw = conicConformalRaw
geoConicEqualAreaRaw = conicEqualAreaRaw
geoConicEquidistantRaw = conicEquidistantRaw
geoEqualEarthRaw = equalEarthRaw
geoEquirectangularRaw = equirectangularRaw
geoGnomonicRaw = gnomonicRaw
geoMercatorRaw = mercatorRaw
geoNaturalEarth1Raw = naturalEarth1Raw
geoOrthographicRaw = orthographicRaw
geoStereographicRaw = stereographicRaw
geoTransverseMercatorRaw = transverseMercatorRaw


def geoArea(obj: Any) -> float:
    return geo_area_from_stream(obj)


def geoBounds(obj: Any) -> list[list[float]]:
    return geo_bounds_from_stream(obj)


def geoCentroid(obj: Any) -> list[float]:
    return geo_centroid_from_stream(obj)


geoClipAntimeridian = clip_antimeridian


def geoClipCircle(radius: float) -> Any:
    return clip_circle(radius)


def geoClipRectangle(x0: float, y0: float, x1: float, y1: float) -> Any:
    return clip_rectangle(x0, y0, x1, y1)


def geoClipExtent():
    extent = [[0, 0], [960, 500]]

    def clip(stream: Any):
        return geoClipRectangle(extent[0][0], extent[0][1], extent[1][0], extent[1][1])(
            stream
        )

    def extent_method(v: Any = _MISSING):
        nonlocal extent
        if v is _MISSING:
            return extent
        extent = v
        return clip

    clip.extent = extent_method  # type: ignore[attr-defined]
    return clip


def geoGraticule():
    return geo_graticule_factory()


def geoGraticule10():
    return geo_graticule_factory()()
