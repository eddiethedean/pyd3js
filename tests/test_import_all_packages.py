from __future__ import annotations

import importlib
import json
from pathlib import Path


def test_import_every_subpackage() -> None:
    root = Path(__file__).resolve().parents[1]
    manifest = json.loads((root / "scripts" / "package_manifest.json").read_text())
    for row in manifest:
        importlib.import_module(row["import"])
    importlib.import_module("pyd3js")
