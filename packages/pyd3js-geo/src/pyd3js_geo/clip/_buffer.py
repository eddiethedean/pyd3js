"""d3-geo `clip/buffer.js`."""

from __future__ import annotations

from typing import Any


def noop(*_a: Any, **_k: Any) -> None:
    return None


class ClipBuffer:
    __slots__ = ("_lines", "_line")

    def __init__(self) -> None:
        self._lines: list[list[list[float | None]]] = []
        self._line: list[list[float | None]] | None = None

    def point(self, x: float, y: float, m: Any = None) -> None:
        assert self._line is not None
        self._line.append([x, y, m])

    def lineStart(self) -> None:
        self._line = []
        self._lines.append(self._line)

    def lineEnd(self) -> None:
        return None

    def rejoin(self) -> None:
        if len(self._lines) > 1:
            last = self._lines.pop()
            first = self._lines.pop(0)
            self._lines.append(last + first)

    def result(self) -> list[list[list[float | None]]]:
        out = self._lines
        self._lines = []
        self._line = None
        return out


def clip_buffer() -> ClipBuffer:
    return ClipBuffer()
