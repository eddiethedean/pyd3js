# ruff: noqa: E741 — D3 uses `l` for HSL lightness / generic luminance labels.
"""RGB/HSL color spaces — port of d3-color `color.js`."""

from __future__ import annotations

import math
import re
from typing import Any

from pyd3js_color._named_colors import NAMED

DARKER = 0.7
BRIGHTER = 1.0 / DARKER

_RE_I = r"\s*([+-]?\d+)\s*"
_RE_N = r"\s*([+-]?(?:\d*\.)?\d+(?:[eE][+-]?\d+)?)\s*"
_RE_P = r"\s*([+-]?(?:\d*\.)?\d+(?:[eE][+-]?\d+)?)%\s*"

_RE_HEX = re.compile(r"^#([0-9a-f]{3,8})$")
_RE_RGB_INTEGER = re.compile(rf"^rgb\({_RE_I},{_RE_I},{_RE_I}\)$")
_RE_RGB_PERCENT = re.compile(rf"^rgb\({_RE_P},{_RE_P},{_RE_P}\)$")
_RE_RGBA_INTEGER = re.compile(rf"^rgba\({_RE_I},{_RE_I},{_RE_I},{_RE_N}\)$")
_RE_RGBA_PERCENT = re.compile(rf"^rgba\({_RE_P},{_RE_P},{_RE_P},{_RE_N}\)$")
_RE_HSL_PERCENT = re.compile(rf"^hsl\({_RE_N},{_RE_P},{_RE_P}\)$")
_RE_HSLA_PERCENT = re.compile(rf"^hsla\({_RE_N},{_RE_P},{_RE_P},{_RE_N}\)$")


def _unary_plus(x: Any) -> float:
    """Match JavaScript unary `+` (`ToNumber`)."""
    if x is None:
        return 0.0
    if isinstance(x, bool):
        return 1.0 if x else 0.0
    if isinstance(x, (int, float)):
        return float(x)
    if isinstance(x, str):
        s = x.strip()
        if s == "":
            return float("nan")
        try:
            return float(s)
        except ValueError:
            return float("nan")
    return float("nan")


def _rgbn(n: int) -> Rgb:
    return Rgb((n >> 16) & 0xFF, (n >> 8) & 0xFF, n & 0xFF, 1.0)


def _rgba(r: float, g: float, b: float, a: float) -> Rgb:
    if a <= 0:
        r = g = b = float("nan")
    return Rgb(r, g, b, a)


def _hsla(h: float, s: float, l: float, a: float) -> Hsl:
    if a <= 0:
        h = s = l = float("nan")
    elif l <= 0 or l >= 1:
        h = s = float("nan")
    elif s <= 0:
        h = float("nan")
    return Hsl(h, s, l, a)


def _hex_byte(v: float) -> str:
    iv = _clampi(v)
    return ("0" if iv < 16 else "") + format(iv, "x")


def _js_round(value: float) -> int:
    """Match `Math.round` (ECMAScript)."""
    if math.isnan(value):
        return 0
    return int(math.floor(value + 0.5))


def _clampi(value: float) -> int:
    r = _js_round(value)
    return max(0, min(255, r or 0))


def _clampa(opacity: float) -> float:
    if math.isnan(opacity):
        return 1.0
    return max(0.0, min(1.0, opacity))


def _clamph(value: float) -> float:
    v = (value or 0.0) % 360.0
    return v + 360.0 if v < 0 else v


def _clampt(value: float) -> float:
    return max(0.0, min(1.0, value or 0.0))


def _js_number_str(x: float) -> str:
    """Format a float like JavaScript default `String(number)` for JSON-safe values."""
    if math.isnan(x):
        return "NaN"
    if math.isinf(x):
        return "Infinity" if x > 0 else "-Infinity"
    rx = round(x)
    if abs(x - rx) < 1e-12:
        return str(int(rx))
    s = format(x, ".16g")
    if "e" in s or "E" in s:
        return s  # pragma: no cover — CSS color strings rarely use scientific notation
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def hsl2rgb(h: float, m1: float, m2: float) -> float:
    """From FvD 13.37, CSS Color Module Level 3 (`h` in [0, 360))."""
    if h < 60:
        return (m1 + (m2 - m1) * h / 60.0) * 255.0
    if h < 180:
        return m2 * 255.0
    if h < 240:
        return (m1 + (m2 - m1) * (240.0 - h) / 60.0) * 255.0
    return m1 * 255.0


def _hue_norm(h: float) -> float:
    """Match JS `this.h % 360 + (this.h < 0) * 360` for doubles."""
    x = math.fmod(h, 360.0)
    if h < 0:
        x += 360.0
    return x


class Color:
    """Abstract base for D3 color spaces."""

    def rgb(self) -> Rgb:
        raise NotImplementedError

    def displayable(self) -> bool:
        return self.rgb().displayable()

    def formatHex(self) -> str:
        return self.rgb().formatHex()

    def formatHex8(self) -> str:
        return self.rgb().formatHex8()

    def formatHsl(self) -> str:
        return hslConvert(self).formatHsl()

    def formatRgb(self) -> str:
        return self.rgb().formatRgb()

    def copy(self, **channels: Any) -> Color:
        cls = type(self)
        o = cls.__new__(cls)
        slots = getattr(cls, "__slots__", None)
        if slots:
            for name in slots:
                setattr(o, name, getattr(self, name))
        else:
            o.__dict__.update(self.__dict__)  # pragma: no cover
        for k, v in channels.items():
            setattr(o, k, _unary_plus(v))
        return o

    @property
    def hex(self) -> str:
        """Deprecated alias for `formatHex`."""
        return self.formatHex()

    def __str__(self) -> str:
        return self.formatRgb()


class Rgb(Color):
    __slots__ = ("r", "g", "b", "opacity")

    def __init__(self, r: Any, g: Any, b: Any, opacity: Any = 1.0) -> None:
        self.r = _unary_plus(r)
        self.g = _unary_plus(g)
        self.b = _unary_plus(b)
        op = opacity
        self.opacity = 1.0 if op is None else _unary_plus(op)

    def brighter(self, k: float | None = None) -> Rgb:
        kk = BRIGHTER if k is None else BRIGHTER**k
        return Rgb(self.r * kk, self.g * kk, self.b * kk, self.opacity)

    def darker(self, k: float | None = None) -> Rgb:
        kk = DARKER if k is None else DARKER**k
        return Rgb(self.r * kk, self.g * kk, self.b * kk, self.opacity)

    def rgb(self) -> Rgb:
        return self

    def clamp(self) -> Rgb:
        return Rgb(
            _clampi(self.r), _clampi(self.g), _clampi(self.b), _clampa(self.opacity)
        )

    def displayable(self) -> bool:
        return (
            (-0.5 <= self.r < 255.5)
            and (-0.5 <= self.g < 255.5)
            and (-0.5 <= self.b < 255.5)
            and (0.0 <= self.opacity <= 1.0)
        )

    def formatHex(self) -> str:
        return f"#{_hex_byte(self.r)}{_hex_byte(self.g)}{_hex_byte(self.b)}"

    def formatHex8(self) -> str:
        op = self.opacity
        a = op if not math.isnan(op) else 1.0
        return (
            f"#{_hex_byte(self.r)}{_hex_byte(self.g)}{_hex_byte(self.b)}"
            f"{_hex_byte(a * 255)}"
        )

    def formatRgb(self) -> str:
        a = _clampa(self.opacity)
        if a == 1.0:
            return f"rgb({_clampi(self.r)}, {_clampi(self.g)}, {_clampi(self.b)})"
        return f"rgba({_clampi(self.r)}, {_clampi(self.g)}, {_clampi(self.b)}, {_js_number_str(a)})"


class Hsl(Color):
    __slots__ = ("h", "s", "l", "opacity")

    def __init__(self, h: Any, s: Any, l: Any, opacity: Any = 1.0) -> None:
        self.h = _unary_plus(h)
        self.s = _unary_plus(s)
        self.l = _unary_plus(l)
        op = opacity
        self.opacity = 1.0 if op is None else _unary_plus(op)

    def brighter(self, k: float | None = None) -> Hsl:
        kk = BRIGHTER if k is None else BRIGHTER**k
        return Hsl(self.h, self.s, self.l * kk, self.opacity)

    def darker(self, k: float | None = None) -> Hsl:
        kk = DARKER if k is None else DARKER**k
        return Hsl(self.h, self.s, self.l * kk, self.opacity)

    def rgb(self) -> Rgb:
        h = _hue_norm(self.h)
        s = 0.0 if (math.isnan(h) or math.isnan(self.s)) else self.s
        l = self.l
        m2 = l + (l if l < 0.5 else 1.0 - l) * s
        m1 = 2.0 * l - m2
        hr = h - 240.0 if h >= 240.0 else h + 120.0
        hg = h
        hb = h + 240.0 if h < 120.0 else h - 120.0
        return Rgb(
            hsl2rgb(hr, m1, m2),
            hsl2rgb(hg, m1, m2),
            hsl2rgb(hb, m1, m2),
            self.opacity,
        )

    def clamp(self) -> Hsl:
        return Hsl(
            _clamph(self.h), _clampt(self.s), _clampt(self.l), _clampa(self.opacity)
        )

    def displayable(self) -> bool:
        return (
            ((0.0 <= self.s <= 1.0) or math.isnan(self.s))
            and (0.0 <= self.l <= 1.0)
            and (0.0 <= self.opacity <= 1.0)
        )

    def formatHsl(self) -> str:
        a = _clampa(self.opacity)
        ch = _clamph(self.h)
        cs = _clampt(self.s) * 100.0
        cl = _clampt(self.l) * 100.0
        if a == 1.0:
            return f"hsl({_js_number_str(ch)}, {_js_number_str(cs)}%, {_js_number_str(cl)}%)"
        return (
            f"hsla({_js_number_str(ch)}, {_js_number_str(cs)}%, "
            f"{_js_number_str(cl)}%, {_js_number_str(a)})"
        )


def hslConvert(o: Any) -> Hsl:
    if isinstance(o, Hsl):
        return Hsl(o.h, o.s, o.l, o.opacity)
    if not isinstance(o, Color):
        o = color(o)
    if o is None:
        return Hsl(float("nan"), float("nan"), float("nan"), float("nan"))
    if isinstance(o, Hsl):
        return o
    o = o.rgb()
    r = o.r / 255.0
    g = o.g / 255.0
    b = o.b / 255.0
    minimum = min(r, g, b)
    maximum = max(r, g, b)
    h = float("nan")
    s = maximum - minimum
    l = (maximum + minimum) / 2.0
    if s:
        if r == maximum:
            h = (g - b) / s + (6.0 if g < b else 0.0)
        elif g == maximum:
            h = (b - r) / s + 2.0
        else:
            h = (r - g) / s + 4.0
        s /= minimum + maximum if l < 0.5 else 2.0 - maximum - minimum
        h *= 60.0
    else:
        s = 0.0 if l > 0 and l < 1 else h
    return Hsl(h, s, l, o.opacity)


def hsl(*args: Any) -> Hsl:
    if len(args) == 1:
        return hslConvert(args[0])
    if len(args) == 3:
        h, s, l = args
        return Hsl(h, s, l, 1.0)
    if len(args) == 4:
        h, s, l, opacity = args
        return Hsl(h, s, l, 1.0 if opacity is None else opacity)
    return Hsl(float("nan"), float("nan"), float("nan"), float("nan"))


def rgbConvert(o: Any) -> Rgb:
    if isinstance(o, Color):
        pass
    else:
        o = color(o)
    if o is None:
        return Rgb(float("nan"), float("nan"), float("nan"), float("nan"))
    o = o.rgb()
    return Rgb(o.r, o.g, o.b, o.opacity)


def rgb(*args: Any) -> Rgb:
    if len(args) == 1:
        return rgbConvert(args[0])
    if len(args) == 3:
        r, g, b = args
        return Rgb(r, g, b, 1.0)
    if len(args) == 4:
        r, g, b, opacity = args
        return Rgb(r, g, b, 1.0 if opacity is None else opacity)
    return Rgb(float("nan"), float("nan"), float("nan"), float("nan"))


def color(spec: Any) -> Rgb | Hsl | None:
    if isinstance(spec, Color):
        fmt = spec.formatRgb()
    else:
        fmt = str(spec).strip().lower()

    m = _RE_HEX.match(fmt)
    if m:
        raw = m.group(1)
        ln = len(raw)
        value = int(raw, 16)
        if ln == 6:
            return _rgbn(value)
        if ln == 3:
            return Rgb(
                ((value >> 8) & 0xF) | ((value >> 4) & 0xF0),
                ((value >> 4) & 0xF) | (value & 0xF0),
                ((value & 0xF) << 4) | (value & 0xF),
                1.0,
            )
        if ln == 8:
            return _rgba(
                (value >> 24) & 0xFF,
                (value >> 16) & 0xFF,
                (value >> 8) & 0xFF,
                (value & 0xFF) / 255.0,
            )
        if ln == 4:
            return _rgba(
                ((value >> 12) & 0xF) | ((value >> 8) & 0xF0),
                ((value >> 8) & 0xF) | ((value >> 4) & 0xF0),
                ((value >> 4) & 0xF) | (value & 0xF0),
                (((value & 0xF) << 4) | (value & 0xF)) / 255.0,
            )
        return None

    m = _RE_RGB_INTEGER.match(fmt)
    if m:
        return Rgb(float(m.group(1)), float(m.group(2)), float(m.group(3)), 1.0)

    m = _RE_RGB_PERCENT.match(fmt)
    if m:
        return Rgb(
            float(m.group(1)) * 255.0 / 100.0,
            float(m.group(2)) * 255.0 / 100.0,
            float(m.group(3)) * 255.0 / 100.0,
            1.0,
        )

    m = _RE_RGBA_INTEGER.match(fmt)
    if m:
        return _rgba(
            float(m.group(1)),
            float(m.group(2)),
            float(m.group(3)),
            float(m.group(4)),
        )

    m = _RE_RGBA_PERCENT.match(fmt)
    if m:
        return _rgba(
            float(m.group(1)) * 255.0 / 100.0,
            float(m.group(2)) * 255.0 / 100.0,
            float(m.group(3)) * 255.0 / 100.0,
            float(m.group(4)),
        )

    m = _RE_HSL_PERCENT.match(fmt)
    if m:
        return _hsla(
            float(m.group(1)),
            float(m.group(2)) / 100.0,
            float(m.group(3)) / 100.0,
            1.0,
        )

    m = _RE_HSLA_PERCENT.match(fmt)
    if m:
        return _hsla(
            float(m.group(1)),
            float(m.group(2)) / 100.0,
            float(m.group(3)) / 100.0,
            float(m.group(4)),
        )

    if fmt in NAMED:
        return _rgbn(NAMED[fmt])
    if fmt == "transparent":
        return Rgb(float("nan"), float("nan"), float("nan"), 0.0)
    return None
