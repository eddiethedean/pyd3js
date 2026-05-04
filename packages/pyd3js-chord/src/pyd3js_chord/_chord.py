from __future__ import annotations

from dataclasses import dataclass
from functools import cmp_to_key
from typing import Any, Callable, Optional, Protocol, Sequence, TypeVar, cast

from pyd3js_chord._math import max_, tau

T = TypeVar("T")


def _range(i: int, j: int) -> list[int]:
    return list(range(i, j))


class _Compare(Protocol):
    def __call__(self, a: float, b: float) -> float: ...


def _compare_value(compare: _Compare):
    def _cmp(a: dict[str, Any], b: dict[str, Any]) -> float:
        av = float(a["source"]["value"]) + float(a["target"]["value"])
        bv = float(b["source"]["value"]) + float(b["target"]["value"])
        return float(compare(av, bv))

    return _cmp


class Chords(list):
    groups: list[dict[str, Any]]


@dataclass
class _ChordGen:
    directed: bool
    transpose: bool
    padAngle_: float = 0.0
    sortGroups_: Optional[Callable[[float, float], float]] = None
    sortSubgroups_: Optional[Callable[[float, float], float]] = None
    sortChords_: Optional[Callable[[dict[str, Any], dict[str, Any]], float]] = None
    sortChords_input_: Optional[Callable[[float, float], float]] = None

    def __call__(self, matrix: Sequence[Sequence[int | float]]) -> Chords:
        n = len(matrix)
        groupSums = [0.0] * n
        groupIndex = _range(0, n)
        chords: list[Optional[dict[str, Any]]] = [None] * (n * n)
        groups: list[dict[str, Any] | None] = [None] * n

        # Flatten matrix (transpose if requested).
        flat: list[float] = [0.0] * (n * n)
        for i in range(n * n):
            if self.transpose:
                flat[i] = float(matrix[i % n][i // n])
            else:
                flat[i] = float(matrix[i // n][i % n])

        k_sum = 0.0
        for i in range(n):
            x = 0.0
            for j in range(n):
                x += flat[i * n + j] + (1.0 if self.directed else 0.0) * flat[j * n + i]
            groupSums[i] = x
            k_sum += x

        k = max_(0.0, tau - self.padAngle_ * n) / k_sum if k_sum else 0.0
        dx = self.padAngle_ if k else tau / n

        x = 0.0
        if self.sortGroups_ is not None:
            sort_groups = self.sortGroups_
            groupIndex.sort(
                key=cmp_to_key(
                    lambda a, b: (
                        -1
                        if sort_groups(groupSums[a], groupSums[b]) < 0
                        else 1
                        if sort_groups(groupSums[a], groupSums[b]) > 0
                        else 0
                    )
                )
            )

        for i in groupIndex:
            x0 = x
            if self.directed:
                subgroupIndex = [
                    j
                    for j in _range(~n + 1, n)
                    if (flat[(~j) * n + i] if j < 0 else flat[i * n + j])
                ]
                if self.sortSubgroups_ is not None:
                    sort_sub = self.sortSubgroups_

                    def _sub_val(j: int) -> float:
                        return -flat[(~j) * n + i] if j < 0 else flat[i * n + j]

                    subgroupIndex.sort(
                        key=cmp_to_key(
                            lambda a, b: (
                                -1
                                if sort_sub(_sub_val(a), _sub_val(b)) < 0
                                else 1
                                if sort_sub(_sub_val(a), _sub_val(b)) > 0
                                else 0
                            )
                        )
                    )

                for j in subgroupIndex:
                    if j < 0:
                        idx = (~j) * n + i
                        ch = chords[idx] or {"source": None, "target": None}
                        chords[idx] = ch
                        value = flat[idx]
                        ch["target"] = {
                            "index": i,
                            "startAngle": x,
                            "endAngle": x + value * k,
                            "value": value,
                        }
                        x += value * k
                    else:
                        idx = i * n + j
                        ch = chords[idx] or {"source": None, "target": None}
                        chords[idx] = ch
                        value = flat[idx]
                        ch["source"] = {
                            "index": i,
                            "startAngle": x,
                            "endAngle": x + value * k,
                            "value": value,
                        }
                        x += value * k

                groups[i] = {
                    "index": i,
                    "startAngle": x0,
                    "endAngle": x,
                    "value": groupSums[i],
                }
            else:
                subgroupIndex = [
                    j for j in _range(0, n) if flat[i * n + j] or flat[j * n + i]
                ]
                if self.sortSubgroups_ is not None:
                    sort_sub = self.sortSubgroups_
                    subgroupIndex.sort(
                        key=cmp_to_key(
                            lambda a, b: (
                                -1
                                if sort_sub(flat[i * n + a], flat[i * n + b]) < 0
                                else 1
                                if sort_sub(flat[i * n + a], flat[i * n + b]) > 0
                                else 0
                            )
                        )
                    )

                for j in subgroupIndex:
                    if i < j:
                        idx = i * n + j
                        ch = chords[idx] or {"source": None, "target": None}
                        chords[idx] = ch
                        value = flat[idx]
                        ch["source"] = {
                            "index": i,
                            "startAngle": x,
                            "endAngle": x + value * k,
                            "value": value,
                        }
                        x += value * k
                    else:
                        idx = j * n + i
                        ch = chords[idx] or {"source": None, "target": None}
                        chords[idx] = ch
                        value = flat[i * n + j]
                        ch["target"] = {
                            "index": i,
                            "startAngle": x,
                            "endAngle": x + value * k,
                            "value": value,
                        }
                        x += value * k
                        if i == j:
                            ch["source"] = ch["target"]

                    ch = chords[idx]
                    assert ch is not None
                    if (
                        ch["source"] is not None
                        and ch["target"] is not None
                        and ch["source"]["value"] < ch["target"]["value"]
                    ):
                        ch["source"], ch["target"] = (ch["target"], ch["source"])

                groups[i] = {
                    "index": i,
                    "startAngle": x0,
                    "endAngle": x,
                    "value": groupSums[i],
                }

            x += dx

        out = Chords([c for c in chords if c is not None])
        out.groups = cast(list[dict[str, Any]], groups)

        if self.sortChords_ is not None:
            cmp = self.sortChords_

            def _cmp(a: dict[str, Any], b: dict[str, Any]) -> int:
                v = float(cmp(a, b))
                return -1 if v < 0 else 1 if v > 0 else 0

            out.sort(key=cmp_to_key(_cmp))
        return out

    def padAngle(self, *args: Any):
        if len(args) == 0:
            return self.padAngle_
        (value,) = args
        self.padAngle_ = max_(0.0, float(value))
        return self

    def sortGroups(self, *args: Any):
        if len(args) == 0:
            return self.sortGroups_
        (value,) = args
        self.sortGroups_ = value
        return self

    def sortSubgroups(self, *args: Any):
        if len(args) == 0:
            return self.sortSubgroups_
        (value,) = args
        self.sortSubgroups_ = value
        return self

    def sortChords(self, *args: Any):
        if len(args) == 0:
            return self.sortChords_input_
        (value,) = args
        if value is None:
            self.sortChords_ = None
            self.sortChords_input_ = None
            return self
        self.sortChords_input_ = value
        self.sortChords_ = _compare_value(value)
        return self


def chord() -> _ChordGen:
    return _ChordGen(directed=False, transpose=False)


def chordTranspose() -> _ChordGen:
    return _ChordGen(directed=False, transpose=True)


def chordDirected() -> _ChordGen:
    return _ChordGen(directed=True, transpose=False)
