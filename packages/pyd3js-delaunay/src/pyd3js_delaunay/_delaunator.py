"""Mapbox Delaunator — mesh via Node (`delaunator@5.x`) for parity with d3-delaunay's dependency."""

from __future__ import annotations

import json
import os
import subprocess
from array import array
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Callable, Union


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _node_executable() -> str:
    return os.environ.get("NODE_EXECUTABLE", "node")


def _mesh_script() -> Path:
    return Path(__file__).resolve().parents[2] / "scripts" / "delaunator_mesh.mjs"


def _run_node_delaunator(coords: array) -> dict[str, list[int]]:
    script = _mesh_script()
    if not script.is_file():
        raise FileNotFoundError(f"Missing mesh script: {script}")
    bundled = (
        _repo_root()
        / "tools"
        / "oracle"
        / "node_modules"
        / "delaunator"
        / "index.js"
    )
    if not bundled.is_file():
        raise FileNotFoundError(
            f"delaunator not found at {bundled}. Run: cd tools/oracle && npm install"
        )
    proc = subprocess.run(
        [_node_executable(), str(script)],
        input=json.dumps([float(x) for x in coords]),
        text=True,
        capture_output=True,
        cwd=str(_repo_root()),
        env=os.environ.copy(),
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "node delaunator failed")
    return json.loads(proc.stdout)


def default_get_x(p: Any, _i: int = 0, _points: Any = None) -> float:
    return float(p[0])


def default_get_y(p: Any, _i: int = 0, _points: Any = None) -> float:
    return float(p[1])


def flat_array(
    points: Sequence[Any],
    fx: Callable[[Any, int, Sequence[Any]], float],
    fy: Callable[[Any, int, Sequence[Any]], float],
    that: Any,
) -> array:
    n = len(points)
    out = array("d", [0.0]) * (n * 2)
    for i in range(n):
        p = points[i]
        out[2 * i] = float(fx(p, i, points))
        out[2 * i + 1] = float(fy(p, i, points))
    return out


def flat_iterable(
    points: Iterable[Any],
    fx: Callable[[Any, int, Any], float],
    fy: Callable[[Any, int, Any], float],
    that: Any,
) -> array:
    plist = list(points)
    coords_list: list[float] = []
    i = 0
    for p in plist:
        coords_list.append(float(fx(p, i, plist)))
        coords_list.append(float(fy(p, i, plist)))
        i += 1
    return array("d", coords_list)


class Delaunator:
    """Triangulation graph matching npm `delaunator` (half-edges, hull, triangles)."""

    coords: array
    triangles: array
    halfedges: array
    hull: array

    def __init__(self, coords: Union[array, Sequence[float]]) -> None:
        if isinstance(coords, array):
            self.coords = coords
        else:
            self.coords = array("d", list(coords))

        n = len(self.coords) >> 1
        if n > 0 and not isinstance(self.coords[0], (int, float)):
            raise ValueError("Expected coords to contain numbers.")

        self._sync_from_mesh()

    def _sync_from_mesh(self) -> None:
        data = _run_node_delaunator(self.coords)
        self.triangles = array("I", data["triangles"])
        self.halfedges = array("i", data["halfedges"])
        self.hull = array("I", data["hull"])

    def update(self) -> Delaunator:
        self._sync_from_mesh()
        return self

    @classmethod
    def from_points(
        cls,
        points: Union[Sequence[Any], Iterable[Any]],
        fx: Callable[[Any, int, Any], float] | None = None,
        fy: Callable[[Any, int, Any], float] | None = None,
        that: Any = None,
    ) -> Delaunator:
        if fx is None:
            fx = default_get_x
        if fy is None:
            fy = default_get_y
        if hasattr(points, "__len__") and not isinstance(points, (str, bytes)):
            seq = points  # type: ignore[arg-type]
            return cls(flat_array(seq, fx, fy, that))
        return cls(flat_iterable(points, fx, fy, that))
