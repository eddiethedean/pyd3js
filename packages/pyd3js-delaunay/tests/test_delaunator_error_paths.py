from __future__ import annotations

from array import array
from pathlib import Path
from types import SimpleNamespace

import pytest

import pyd3js_delaunay._delaunator as delaunator_mod


def test_run_node_delaunator_missing_mesh_script(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(delaunator_mod, "_mesh_script", lambda: Path("/nope/not_there.mjs"))
    with pytest.raises(FileNotFoundError, match="Missing mesh script"):
        delaunator_mod._run_node_delaunator(array("d", [0.0, 0.0]))


def test_run_node_delaunator_missing_bundled_delaunator(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Make the mesh script exist, but ensure the bundled delaunator path does not.
    script = tmp_path / "mesh.mjs"
    script.write_text("// noop", encoding="utf-8")
    monkeypatch.setattr(delaunator_mod, "_mesh_script", lambda: script)
    monkeypatch.setattr(delaunator_mod, "_repo_root", lambda: tmp_path)
    with pytest.raises(FileNotFoundError, match="delaunator not found"):
        delaunator_mod._run_node_delaunator(array("d", [0.0, 0.0]))


def test_run_node_delaunator_subprocess_failure(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    # Make both files exist; then force subprocess to fail.
    script = tmp_path / "mesh.mjs"
    script.write_text("// noop", encoding="utf-8")
    bundled = tmp_path / "tools" / "oracle" / "node_modules" / "delaunator" / "index.js"
    bundled.parent.mkdir(parents=True, exist_ok=True)
    bundled.write_text("// noop", encoding="utf-8")
    monkeypatch.setattr(delaunator_mod, "_mesh_script", lambda: script)
    monkeypatch.setattr(delaunator_mod, "_repo_root", lambda: tmp_path)
    monkeypatch.setattr(
        delaunator_mod.subprocess,
        "run",
        lambda *a, **k: SimpleNamespace(returncode=1, stderr="boom", stdout=""),
    )
    with pytest.raises(RuntimeError, match="boom"):
        delaunator_mod._run_node_delaunator(array("d", [0.0, 0.0]))


def test_delaunator_init_non_array_coords_and_sync(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        delaunator_mod,
        "_run_node_delaunator",
        lambda coords: {"triangles": [0, 1, 2], "halfedges": [-1, -1, -1], "hull": [0, 1, 2]},
    )
    d = delaunator_mod.Delaunator([0.0, 0.0, 1.0, 0.0, 0.0, 1.0])
    assert list(d.hull) == [0, 1, 2]
    d.update()
    assert len(d.triangles) == 3


def test_delaunator_rejects_non_numeric_array_contents(monkeypatch: pytest.MonkeyPatch) -> None:
    # If coords is already an array (not coerced), we can trigger the ValueError guard.
    monkeypatch.setattr(
        delaunator_mod,
        "_run_node_delaunator",
        lambda coords: {"triangles": [], "halfedges": [], "hull": []},
    )
    bad = array("u", "abcd")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="Expected coords to contain numbers"):
        delaunator_mod.Delaunator(bad)  # type: ignore[arg-type]


def test_delaunator_from_points_sequence_and_iterable(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        delaunator_mod,
        "_run_node_delaunator",
        lambda coords: {"triangles": [0, 1, 2], "halfedges": [-1, -1, -1], "hull": [0, 1, 2]},
    )

    d1 = delaunator_mod.Delaunator.from_points([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)])
    assert len(d1.coords) == 6

    def gen():
        yield (0.0, 0.0)
        yield (1.0, 0.0)
        yield (0.0, 1.0)

    d2 = delaunator_mod.Delaunator.from_points(gen())
    assert len(d2.coords) == 6

