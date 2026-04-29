"""D3-compatible `blur`, `blur2`, and `blurImage`."""

from __future__ import annotations

import math
from collections.abc import Callable, MutableSequence
from typing import Any, Protocol, TypedDict, cast


class _BlurData(TypedDict, total=False):
    data: MutableSequence[float]
    width: int
    height: int


def blur(values: MutableSequence[float], r: float) -> MutableSequence[float]:
    """Blur a 1D array in-place.

    Mirrors `d3.blur(values, r)`.
    """

    r = float(r)
    if not (r >= 0):
        raise ValueError("invalid r")

    length = int(math.floor(len(values)))
    if length < 0:
        raise ValueError("invalid length")
    if length == 0 or r == 0:
        return values

    f = _blurf(r)
    temp = list(values)
    f(values, temp, 0, length, 1)
    f(temp, values, 0, length, 1)
    f(values, temp, 0, length, 1)
    return values


def blur2(data: _BlurData, rx: float, ry: float | None = None) -> _BlurData:
    """Blur a 2D grid in-place.

    Mirrors `d3.blur2({data,width[,height]}, rx[,ry])`.
    """

    return _Blur2(_blurf)(data, rx, ry)


def blurImage(data: _BlurData, rx: float, ry: float | None = None) -> _BlurData:
    """Blur an RGBA image buffer in-place.

    Mirrors `d3.blurImage(imageData, rx[,ry])`.
    """

    return _Blur2(_blurf_image)(data, rx, ry)


def _Blur2(blur_factory: Callable[[float], Callable[..., None]]):
    def inner(data: _BlurData, rx: float, ry: float | None = None) -> _BlurData:
        rx = float(rx)
        if not (rx >= 0):
            raise ValueError("invalid rx")
        if ry is None:
            ry = rx
        ry = float(ry)
        if not (ry >= 0):
            raise ValueError("invalid ry")

        values = cast(MutableSequence[float], data["data"])
        width = int(math.floor(int(data["width"])))
        if width < 0:
            raise ValueError("invalid width")

        height_raw = data.get("height", None)
        if height_raw is None:
            height = int(math.floor(len(values) / width)) if width else 0
        else:
            height = int(math.floor(int(height_raw)))
        if height < 0:
            raise ValueError("invalid height")

        if width == 0 or height == 0 or (rx == 0 and ry == 0):
            return data

        blurx = blur_factory(rx) if rx else None
        blury = blur_factory(ry) if ry else None

        temp = list(values)
        if blurx and blury:
            _blurh(blurx, temp, values, width, height)
            _blurh(blurx, values, temp, width, height)
            _blurh(blurx, temp, values, width, height)
            _blurv(blury, values, temp, width, height)
            _blurv(blury, temp, values, width, height)
            _blurv(blury, values, temp, width, height)
        elif blurx:
            _blurh(blurx, values, temp, width, height)
            _blurh(blurx, temp, values, width, height)
            _blurh(blurx, values, temp, width, height)
        elif blury:
            _blurv(blury, values, temp, width, height)
            _blurv(blury, temp, values, width, height)
            _blurv(blury, values, temp, width, height)
        return data

    return inner


def _blurh(blur_fn: Callable[..., None], T: MutableSequence[float], S: MutableSequence[float], w: int, h: int) -> None:
    y = 0
    n = w * h
    while y < n:
        blur_fn(T, S, y, y + w, 1)
        y += w


def _blurv(blur_fn: Callable[..., None], T: MutableSequence[float], S: MutableSequence[float], w: int, h: int) -> None:
    n = w * h
    for x in range(w):
        blur_fn(T, S, x, x + n, w)


def _blurf_image(radius: float):
    blur_fn = _blurf(radius)

    def inner(T: MutableSequence[float], S: MutableSequence[float], start: int, stop: int, step: int) -> None:
        start <<= 2
        stop <<= 2
        step <<= 2
        blur_fn(T, S, start + 0, stop + 0, step)
        blur_fn(T, S, start + 1, stop + 1, step)
        blur_fn(T, S, start + 2, stop + 2, step)
        blur_fn(T, S, start + 3, stop + 3, step)

    return inner


def _blurf(radius: float):
    radius0 = int(math.floor(radius))
    if radius0 == radius:
        return _bluri(radius0)
    t = radius - radius0
    w = 2 * radius + 1

    def inner(T: MutableSequence[float], S: MutableSequence[float], start: int, stop: int, step: int) -> None:
        stop -= step
        if stop < start:
            return
        s0 = step * radius0
        s1 = s0 + step
        total = radius0 * S[start]
        j = start + s0
        i = start
        while i < j:
            total += S[min(stop, i)]
            i += step
        i = start
        while i <= stop:
            total += S[min(stop, i + s0)]
            T[i] = (total + t * (S[max(start, i - s1)] + S[min(stop, i + s1)])) / w
            total -= S[max(start, i - s0)]
            i += step

    return inner


def _bluri(radius: int):
    w = 2 * radius + 1

    def inner(T: MutableSequence[float], S: MutableSequence[float], start: int, stop: int, step: int) -> None:
        stop -= step
        if stop < start:
            return
        s = step * radius
        total = radius * S[start]
        j = start + s
        i = start
        while i < j:
            total += S[min(stop, i)]
            i += step
        i = start
        while i <= stop:
            total += S[min(stop, i + s)]
            T[i] = total / w
            total -= S[max(start, i - s)]
            i += step

    return inner


__all__ = ["blur", "blur2", "blurImage"]

