"""Public geo API barrel: projections, path, fit, and passthrough exports."""

from __future__ import annotations

from pyd3js_geo.circle import geoCircle
from pyd3js_geo.contains import geoContains
from pyd3js_geo.distance import geoDistance
from pyd3js_geo.interpolate import geoInterpolate
from pyd3js_geo.length import geoLength
from pyd3js_geo.rotation import geoRotation
from pyd3js_geo.stream import geoStream
from pyd3js_geo.transform import geoTransform

from pyd3js_geo._fit import fitExtent, fitHeight, fitSize, fitWidth
from pyd3js_geo._path_geo import geoPath
from pyd3js_geo._projection_geo import (
    geoAlbers,
    geoAlbersUsa,
    geoArea,
    geoAzimuthalEqualArea,
    geoAzimuthalEqualAreaRaw,
    geoAzimuthalEquidistant,
    geoAzimuthalEquidistantRaw,
    geoBounds,
    geoCentroid,
    geoClipAntimeridian,
    geoClipCircle,
    geoClipExtent,
    geoClipRectangle,
    geoConicConformal,
    geoConicConformalRaw,
    geoConicEqualArea,
    geoConicEqualAreaRaw,
    geoConicEquidistant,
    geoConicEquidistantRaw,
    geoEqualEarth,
    geoEqualEarthRaw,
    geoEquirectangular,
    geoEquirectangularRaw,
    geoGnomonic,
    geoGnomonicRaw,
    geoGraticule,
    geoGraticule10,
    geoIdentity,
    geoMercator,
    geoMercatorRaw,
    geoNaturalEarth1,
    geoNaturalEarth1Raw,
    geoOrthographic,
    geoOrthographicRaw,
    geoProjection,
    geoProjectionMutator,
    geoStereographic,
    geoStereographicRaw,
    geoTransverseMercator,
    geoTransverseMercatorRaw,
)
