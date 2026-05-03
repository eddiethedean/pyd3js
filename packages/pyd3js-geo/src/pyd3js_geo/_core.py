from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, Callable

from pyd3js_array import Adder

from pyd3js_geo._albers_usa import geo_albers_usa
from pyd3js_geo._bounds_geo import geo_bounds_from_stream
from pyd3js_geo._centroid_geo import geo_centroid_from_stream
from pyd3js_geo._circle_geo import geo_circle_factory
from pyd3js_geo._geo_area_stream import geo_area_from_stream
from pyd3js_geo._graticule_geo import geo_graticule_factory
from pyd3js_geo._identity_proj import geo_identity
from pyd3js_geo._mercator_geo import wrap_mercator_projection
from pyd3js_geo._resample import resample_factory
from pyd3js_geo.clip._antimeridian import clip_antimeridian
from pyd3js_geo.clip._circle import clip_circle
from pyd3js_geo.clip._rectangle import clip_rectangle
from pyd3js_geo._path_planar import (
    PathAreaStream,
    PathBoundsStream,
    PathCentroidStream,
    PathContext,
    PathMeasureStream,
)
from pyd3js_geo.polygon_contains import polygon_contains_rings

_MISSING = object()
epsilon = 1e-6
epsilon2 = 1e-12
pi = math.pi
halfPi = pi / 2
quarterPi = pi / 4
tau = pi * 2
degrees = 180 / pi
radians = pi / 180


def noop(*_: Any) -> None:
    return None


def acos(x: float) -> float:
    return 0 if x > 1 else pi if x < -1 else math.acos(x)


def asin(x: float) -> float:
    return halfPi if x > 1 else -halfPi if x < -1 else math.asin(x)


def haversin(x: float) -> float:
    x = math.sin(x / 2)
    return x * x


def sign(x: float) -> int:
    return 1 if x > 0 else -1 if x < 0 else 0


def compose(a: Callable[..., Any], b: Callable[..., Any]) -> Callable[..., Any]:
    def c(*args: Any) -> Any:
        return b(*a(*args))

    if hasattr(a, "invert") and hasattr(b, "invert"):
        c.invert = lambda *args: a.invert(*b.invert(*args))  # type: ignore[attr-defined]
    return c


def geo_compose_project(
    a: Callable[[float, float], list[float]],
    b: Callable[[float, float], list[float]],
) -> Callable[[float, float], list[float]]:
    """d3-geo `compose.js` for forward projections (a then b on [x,y] pairs)."""

    def composed(x: float, y: float) -> list[float]:
        t = a(x, y)
        return b(t[0], t[1])

    if hasattr(a, "invert") and hasattr(b, "invert"):
        def inv(x: float, y: float) -> list[float] | None:
            t = b.invert(x, y)
            if t is None:
                return None
            return a.invert(t[0], t[1])  # type: ignore[misc]

        composed.invert = inv  # type: ignore[attr-defined]
    return composed


def _transform_radians_factory() -> Callable[[Any], Any]:
    return transformer(
        {
            "point": lambda s, x, y, z=None: (
                s.stream.point(x * radians, y * radians, z)
                if z is not None
                else s.stream.point(x * radians, y * radians)
            ),
        }
    )


def _transform_rotate_factory(
    rotate: Callable[[float, float], list[float]],
) -> Callable[[Any], Any]:
    def point_fn(s: Any, x: float, y: float, z: Any = None) -> Any:
        r = rotate(x, y)
        return (
            s.stream.point(r[0], r[1], z)
            if z is not None
            else s.stream.point(r[0], r[1])
        )

    return transformer({"point": point_fn})


def geoStream(obj: Any, stream: Any) -> None:
    if not obj:
        return
    typ = obj.get("type")
    if typ == "Feature":
        geoStream(obj.get("geometry"), stream)
    elif typ == "FeatureCollection":
        for feature in obj.get("features", []):
            geoStream(feature.get("geometry"), stream)
    elif typ == "GeometryCollection":
        for geometry in obj.get("geometries", []):
            geoStream(geometry, stream)
    elif typ == "Sphere":
        stream.sphere()
    elif typ == "Point":
        c = obj.get("coordinates", [])
        stream.point(c[0], c[1], c[2] if len(c) > 2 else None)
    elif typ == "MultiPoint":
        for c in obj.get("coordinates", []):
            stream.point(c[0], c[1], c[2] if len(c) > 2 else None)
    elif typ == "LineString":
        _stream_line(obj.get("coordinates", []), stream, 0)
    elif typ == "MultiLineString":
        for line in obj.get("coordinates", []):
            _stream_line(line, stream, 0)
    elif typ == "Polygon":
        _stream_polygon(obj.get("coordinates", []), stream)
    elif typ == "MultiPolygon":
        for polygon in obj.get("coordinates", []):
            _stream_polygon(polygon, stream)


def _stream_line(coordinates: list[Any], stream: Any, closed: int) -> None:
    stream.lineStart()
    n = len(coordinates) - closed
    for c in coordinates[:n]:
        stream.point(c[0], c[1], c[2] if len(c) > 2 else None)
    stream.lineEnd()


def _stream_polygon(coordinates: list[Any], stream: Any) -> None:
    stream.polygonStart()
    for ring in coordinates:
        _stream_line(ring, stream, 1)
    stream.polygonEnd()


class TransformStream:
    def __init__(self, stream: Any, methods: dict[str, Callable[..., Any]]):
        self.stream = stream
        self._methods = methods

    def point(self, x: float, y: float, z: Any = None) -> None:
        f = self._methods.get("point")
        if f:
            return f(self, x, y, z) if z is not None else f(self, x, y)
        return self.stream.point(x, y) if z is None else self.stream.point(x, y, z)

    def sphere(self) -> None:
        return self._methods.get(
            "sphere", lambda s: getattr(s.stream, "sphere", noop)()
        )(self)

    def lineStart(self) -> None:
        return self._methods.get("lineStart", lambda s: s.stream.lineStart())(self)

    def lineEnd(self) -> None:
        return self._methods.get("lineEnd", lambda s: s.stream.lineEnd())(self)

    def polygonStart(self) -> None:
        return self._methods.get("polygonStart", lambda s: s.stream.polygonStart())(
            self
        )

    def polygonEnd(self) -> None:
        return self._methods.get("polygonEnd", lambda s: s.stream.polygonEnd())(self)


def transformer(
    methods: dict[str, Callable[..., Any]],
) -> Callable[[Any], TransformStream]:
    return lambda stream: TransformStream(stream, methods)


class _GeoTransform:
    def __init__(self, methods: dict[str, Callable[..., Any]]):
        self._methods = methods

    def stream(self, stream: Any) -> TransformStream:
        return transformer(self._methods)(stream)


def geoTransform(methods: dict[str, Callable[..., Any]]) -> _GeoTransform:
    return _GeoTransform(methods)


def rotationIdentity(lambda_: float, phi: float) -> list[float]:
    if abs(lambda_) > pi:
        lambda_ -= round(lambda_ / tau) * tau
    return [lambda_, phi]


rotationIdentity.invert = rotationIdentity  # type: ignore[attr-defined]


def _forward_rotation_lambda(
    delta_lambda: float,
) -> Callable[[float, float], list[float]]:
    def rotation(lambda_: float, phi: float) -> list[float]:
        lambda_ += delta_lambda
        if abs(lambda_) > pi:
            lambda_ -= round(lambda_ / tau) * tau
        return [lambda_, phi]

    return rotation


def _rotation_lambda(delta_lambda: float) -> Callable[[float, float], list[float]]:
    rotation = _forward_rotation_lambda(delta_lambda)
    rotation.invert = _forward_rotation_lambda(-delta_lambda)  # type: ignore[attr-defined]
    return rotation


def _rotation_phi_gamma(
    delta_phi: float, delta_gamma: float
) -> Callable[[float, float], list[float]]:
    cdp, sdp = math.cos(delta_phi), math.sin(delta_phi)
    cdg, sdg = math.cos(delta_gamma), math.sin(delta_gamma)

    def rotation(lambda_: float, phi: float) -> list[float]:
        cp = math.cos(phi)
        x, y, z = math.cos(lambda_) * cp, math.sin(lambda_) * cp, math.sin(phi)
        k = z * cdp + x * sdp
        return [
            math.atan2(y * cdg - k * sdg, x * cdp - z * sdp),
            asin(k * cdg + y * sdg),
        ]

    def invert(lambda_: float, phi: float) -> list[float]:
        cp = math.cos(phi)
        x, y, z = math.cos(lambda_) * cp, math.sin(lambda_) * cp, math.sin(phi)
        k = z * cdg - y * sdg
        return [
            math.atan2(y * cdg + z * sdg, x * cdp + k * sdp),
            asin(k * cdp - x * sdp),
        ]

    rotation.invert = invert  # type: ignore[attr-defined]
    return rotation


def rotateRadians(
    delta_lambda: float, delta_phi: float, delta_gamma: float
) -> Callable[[float, float], list[float]]:
    delta_lambda = math.fmod(delta_lambda, tau)
    if delta_lambda:
        return (
            compose(
                _rotation_lambda(delta_lambda),
                _rotation_phi_gamma(delta_phi, delta_gamma),
            )
            if delta_phi or delta_gamma
            else _rotation_lambda(delta_lambda)
        )
    return (
        _rotation_phi_gamma(delta_phi, delta_gamma)
        if delta_phi or delta_gamma
        else rotationIdentity
    )


def geoRotation(rotate: list[float]) -> Callable[[list[float]], list[float]]:
    rot = rotateRadians(
        rotate[0] * radians,
        rotate[1] * radians,
        (rotate[2] if len(rotate) > 2 else 0) * radians,
    )

    def forward(coordinates: list[float]) -> list[float]:
        c = rot(coordinates[0] * radians, coordinates[1] * radians)
        return [c[0] * degrees, c[1] * degrees]

    def invert(coordinates: list[float]) -> list[float]:
        c = rot.invert(coordinates[0] * radians, coordinates[1] * radians)  # type: ignore[attr-defined]
        return [c[0] * degrees, c[1] * degrees]

    forward.invert = invert  # type: ignore[attr-defined]
    return forward


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
        return self._project_rotate_transform(
            point[0] * radians, point[1] * radians
        )

    def invert(self, point: list[float] | tuple[float, float]) -> list[float] | None:
        if not hasattr(self._raw, "invert"):
            return None
        p = self._project_rotate_transform.invert(point[0], point[1])  # type: ignore[attr-defined]
        if p is None:
            return None
        return [p[0] * degrees, p[1] * degrees]

    def stream(self, stream: Any) -> Any:
        if (
            self._stream_cache is not None
            and self._stream_cache_stream is stream
        ):
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
            (float(value[0]) % 360) * radians,
            (float(value[1]) % 360) * radians,
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
            (float(value[0]) % 360) * radians,
            (float(value[1]) % 360) * radians,
        )
        self._delta_gamma = (float(value[2]) % 360) * radians if len(value) > 2 else 0
        return self._recenter()

    def angle(self, value: Any = _MISSING):
        if value is _MISSING:
            return self._alpha * degrees
        self._alpha = (float(value) % 360) * radians
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


def identity(stream: Any) -> Any:
    return stream


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


azimuthalEqualAreaRaw = azimuthalRaw(
    lambda c: math.sqrt(2 / max(1 + c, epsilon2))
)
azimuthalEqualAreaRaw.invert = azimuthalInvert(lambda z: 2 * asin(z / 2))  # type: ignore[attr-defined]
azimuthalEquidistantRaw = azimuthalRaw(
    lambda c: (
        lambda a: a / math.sin(a) if a else 0
    )(acos(max(-1 + epsilon2, min(1 - epsilon2, c))))
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


def geoInterpolate(a: list[float], b: list[float]):
    x0, y0, x1, y1 = a[0] * radians, a[1] * radians, b[0] * radians, b[1] * radians
    cy0, sy0, cy1, sy1 = math.cos(y0), math.sin(y0), math.cos(y1), math.sin(y1)
    kx0, ky0, kx1, ky1 = (
        cy0 * math.cos(x0),
        cy0 * math.sin(x0),
        cy1 * math.cos(x1),
        cy1 * math.sin(x1),
    )
    d = 2 * asin(math.sqrt(haversin(y1 - y0) + cy0 * cy1 * haversin(x1 - x0)))
    k = math.sin(d)
    if d:

        def interpolate(t: float) -> list[float]:
            t *= d
            B, A = math.sin(t) / k, math.sin(d - t) / k
            x, y, z = A * kx0 + B * kx1, A * ky0 + B * ky1, A * sy0 + B * sy1
            return [
                math.atan2(y, x) * degrees,
                math.atan2(z, math.sqrt(x * x + y * y)) * degrees,
            ]
    else:

        def interpolate(t: float = 0) -> list[float]:
            return [x0 * degrees, y0 * degrees]

    interpolate.distance = d  # type: ignore[attr-defined]
    return interpolate


class _LengthStream:
    def __init__(self):
        self.sum = Adder()
        self.point = noop
        self.lineEnd = noop

    def sphere(self):
        pass

    def polygonStart(self):
        pass

    def polygonEnd(self):
        pass

    def lineStart(self):
        self.point = self._first
        self.lineEnd = self._end

    def _end(self):
        self.point = noop
        self.lineEnd = noop

    def _first(self, lambda_: float, phi: float, z: Any = None):
        self.lambda0 = lambda_ * radians
        phi *= radians
        self.sinPhi0, self.cosPhi0 = math.sin(phi), math.cos(phi)
        self.point = self._point

    def _point(self, lambda_: float, phi: float, z: Any = None):
        lambda_, phi = lambda_ * radians, phi * radians
        sp, cp = math.sin(phi), math.cos(phi)
        delta = abs(lambda_ - self.lambda0)
        cd, sd = math.cos(delta), math.sin(delta)
        x = cp * sd
        y = self.cosPhi0 * sp - self.sinPhi0 * cp * cd
        zz = self.sinPhi0 * sp + self.cosPhi0 * cp * cd
        self.sum.add(math.atan2(math.sqrt(x * x + y * y), zz))
        self.lambda0, self.sinPhi0, self.cosPhi0 = lambda_, sp, cp


def geoLength(obj: Any) -> float:
    s = _LengthStream()
    geoStream(obj, s)
    return float(s.sum)


def geoDistance(a: Sequence[float], b: Sequence[float]) -> float:
    return geoLength({"type": "LineString", "coordinates": [a, b]})


def geoArea(obj: Any) -> float:
    return geo_area_from_stream(obj)


def geoBounds(obj: Any) -> list[list[float]]:
    return geo_bounds_from_stream(obj)


def geoCentroid(obj: Any) -> list[float]:
    return geo_centroid_from_stream(obj)


def _ring_radians(ring: list[list[float]]) -> list[list[float]]:
    out = [[p[0] * radians, p[1] * radians] for p in ring]
    out.pop()
    return out


def _contains_line(coords: list[list[float]], point: Sequence[float]) -> bool:
    ao: float | None = None
    for i, c in enumerate(coords):
        bo = geoDistance(c, point)
        if bo == 0:
            return True
        if i > 0:
            ab = geoDistance(coords[i], coords[i - 1])
            if (
                ab > 0
                and ao is not None
                and ao <= ab
                and bo <= ab
                and (ao + bo - ab) * (1 - ((ao - bo) / ab) ** 2) < epsilon2 * ab
            ):
                return True
        ao = bo
    return False


def _contains_polygon_coords(
    coordinates: list[list[list[float]]], point: Sequence[float]
) -> bool:
    rings = [_ring_radians(r) for r in coordinates]
    pr = [point[0] * radians, point[1] * radians]
    return polygon_contains_rings(rings, pr)


def geoContains(obj: Any, point: Sequence[float]) -> bool:
    typ = obj.get("type") if obj else None
    if typ == "Sphere":
        return True
    if typ == "Feature":
        return geoContains(obj.get("geometry"), point)
    if typ == "FeatureCollection":
        return any(
            geoContains(f.get("geometry"), point) for f in obj.get("features", [])
        )
    if typ == "Point":
        return geoDistance(obj.get("coordinates"), point) == 0
    if typ == "MultiPoint":
        return any(geoDistance(c, point) == 0 for c in obj.get("coordinates", []))
    if typ == "LineString":
        return _contains_line(obj.get("coordinates", []), point)
    if typ == "MultiLineString":
        return any(_contains_line(line, point) for line in obj.get("coordinates", []))
    if typ == "Polygon":
        return _contains_polygon_coords(obj.get("coordinates", []), point)
    if typ == "MultiPolygon":
        return any(
            _contains_polygon_coords(p, point) for p in obj.get("coordinates", [])
        )
    if typ == "GeometryCollection":
        return any(geoContains(g, point) for g in obj.get("geometries", []))
    return False


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


class PathString:
    def __init__(self, digits: int | None = 3):
        self._digits, self._radius, self._, self._line, self._point = (
            digits,
            4.5,
            "",
            math.nan,
            math.nan,
        )

    def pointRadius(self, r):
        self._radius = float(r)
        return self

    def polygonStart(self):
        self._line = 0

    def polygonEnd(self):
        self._line = math.nan

    def lineStart(self):
        self._point = 0

    def lineEnd(self):
        if self._line == 0:
            self._ += "Z"
        self._point = math.nan

    def point(self, x, y, z=None):
        if self._point == 0:
            self._ += f"M{_fmt(x, self._digits)},{_fmt(y, self._digits)}"
            self._point = 1
        elif self._point == 1:
            self._ += f"L{_fmt(x, self._digits)},{_fmt(y, self._digits)}"
        else:
            r = self._radius
            self._ += f"M{_fmt(x, self._digits)},{_fmt(y, self._digits)}m0,{_fmt(r, self._digits)}a{_fmt(r, self._digits)},{_fmt(r, self._digits)} 0 1,1 0,{_fmt(-2 * r, self._digits)}a{_fmt(r, self._digits)},{_fmt(r, self._digits)} 0 1,1 0,{_fmt(2 * r, self._digits)}z"

    def result(self):
        r = self._
        self._ = ""
        return r or None


def _fmt(x: float, digits: int | None) -> str:
    if digits is not None:
        k = 10**digits
        x = (math.floor(x * k + 0.5) if x >= 0 else math.ceil(x * k - 0.5)) / k
    return format(0 if x == 0 else x, ".15g")


class GeoPath:
    """Matches d3 `path/index.js` (planar metrics vs spherical geo* helpers)."""

    def __init__(self, projection: Any = None, context: Any = None):
        self._projection = projection
        self._digits = 3
        self._point_radius: Any = 4.5
        self._context = context
        self._context_stream: Any = None
        self._sync_context_stream()

    def _sync_context_stream(self) -> None:
        if self._context is None:
            ps = PathString(self._digits)
            if not callable(self._point_radius):
                ps.pointRadius(float(self._point_radius))
            self._context_stream = ps
        else:
            pc = PathContext(self._context)
            if not callable(self._point_radius):
                pc.pointRadius(float(self._point_radius))
            self._context_stream = pc

    def __call__(self, obj: Any = None):
        if obj:
            stream = (
                self._projection.stream(self._context_stream)
                if self._projection is not None
                else self._context_stream
            )
            geoStream(obj, stream)
        return self._context_stream.result()

    def projection(self, v: Any = _MISSING):
        if v is _MISSING:
            return self._projection
        self._projection = v
        return self

    def context(self, v: Any = _MISSING):
        if v is _MISSING:
            return self._context
        self._context = v
        self._sync_context_stream()
        return self

    def pointRadius(self, v: Any = _MISSING):
        if v is _MISSING:
            return self._point_radius
        self._point_radius = v
        self._sync_context_stream()
        if self._context is not None and not callable(v):
            if hasattr(self._context_stream, "pointRadius"):
                self._context_stream.pointRadius(float(v))
        return self

    def digits(self, v: Any = _MISSING):
        if v is _MISSING:
            return self._digits
        self._digits = None if v is None else int(math.floor(v))
        if self._context is None:
            ps = PathString(self._digits)
            if not callable(self._point_radius):
                ps.pointRadius(float(self._point_radius))
            self._context_stream = ps
        return self

    def area(self, obj: Any) -> float:
        s = PathAreaStream()
        geoStream(
            obj,
            self._projection.stream(s) if self._projection is not None else s,
        )
        return s.result()

    def measure(self, obj: Any) -> float:
        s = PathMeasureStream()
        geoStream(
            obj,
            self._projection.stream(s) if self._projection is not None else s,
        )
        return s.result()

    def bounds(self, obj: Any) -> list[list[float]]:
        s = PathBoundsStream()
        geoStream(
            obj,
            self._projection.stream(s) if self._projection is not None else s,
        )
        return s.result()

    def centroid(self, obj: Any) -> list[float]:
        s = PathCentroidStream()
        geoStream(
            obj,
            self._projection.stream(s) if self._projection is not None else s,
        )
        return s.result()


def geoPath(projection: Any = None, context: Any = None) -> GeoPath:
    return GeoPath(projection, context)


def _fit_bounds_extent(
    projection: Any, extent: list[list[float]], b: list[list[float]]
) -> None:
    w = extent[1][0] - extent[0][0]
    h = extent[1][1] - extent[0][1]
    k = min(w / (b[1][0] - b[0][0]), h / (b[1][1] - b[0][1]))
    x = extent[0][0] + (w - k * (b[1][0] + b[0][0])) / 2
    y = extent[0][1] + (h - k * (b[1][1] + b[0][1])) / 2
    projection.scale(150 * k).translate([x, y])


def _fit_bounds_width(projection: Any, width: float, b: list[list[float]]) -> None:
    w = float(width)
    k = w / (b[1][0] - b[0][0])
    x = (w - k * (b[1][0] + b[0][0])) / 2
    y = -k * b[0][1]
    projection.scale(150 * k).translate([x, y])


def _fit_bounds_height(projection: Any, height: float, b: list[list[float]]) -> None:
    h = float(height)
    k = h / (b[1][1] - b[0][1])
    x = -k * b[0][0]
    y = (h - k * (b[1][1] + b[0][1])) / 2
    projection.scale(150 * k).translate([x, y])


def _fit(
    projection: Any, fit_bounds: Callable[[list[list[float]]], None], obj: Any
) -> Any:
    clip = projection.clipExtent() if hasattr(projection, "clipExtent") else None
    projection.scale(150).translate([0.0, 0.0])
    if clip is not None:
        projection.clipExtent(None)
    bs = PathBoundsStream()
    geoStream(obj, projection.stream(bs))
    fit_bounds(bs.result())
    if clip is not None:
        projection.clipExtent(clip)
    return projection


def fitExtent(projection: Any, extent: list[list[float]], obj: Any):
    return _fit(
        projection,
        lambda b: _fit_bounds_extent(projection, extent, b),
        obj,
    )


def fitSize(projection: Any, size: list[float], obj: Any):
    return fitExtent(projection, [[0, 0], size], obj)


def fitWidth(projection: Any, width: float, obj: Any):
    return _fit(projection, lambda b: _fit_bounds_width(projection, width, b), obj)


def fitHeight(projection: Any, height: float, obj: Any):
    return _fit(projection, lambda b: _fit_bounds_height(projection, height, b), obj)


def geoCircle():
    return geo_circle_factory()


def geoGraticule():
    return geo_graticule_factory()


def geoGraticule10():
    return geo_graticule_factory()()
