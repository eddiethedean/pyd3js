#!/usr/bin/env python3
"""Generate packages/*/pyproject.toml and src layout from package_manifest.json."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "scripts" / "package_manifest.json"

PYPROJECT_TEMPLATE = """[project]
name = "{dist}"
version = "0.0.0"
description = "Python port of {npm_name}"
requires-python = ">=3.10"
readme = "README.md"
authors = [{{ name = "pyd3 contributors" }}]
dependencies = [
{deps_lines}
]

[build-system]
requires = ["hatchling>=1.18.0"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/{import_name}"]
{uv_sources_block}
"""

README_TEMPLATE = """# {dist}

Python port of [`{npm_name}`](https://github.com/d3/{npm_name}).

Tracked version: see [upstream_lock.json](../../upstream_lock.json).
"""

INIT_TEMPLATE = '''"""
{pydist} — Python port of {npm_name}.
"""

__version__ = "0.0.0"
'''


def dep_lines(deps: list[str]) -> tuple[str, str]:
    if not deps:
        return "    # (no internal pyd3 deps)", ""
    lines = []
    sources = []
    for d in deps:
        lines.append(f'    "{d}>=0.0.0",')
        sources.append(f"{d} = {{ workspace = true }}")
    return "\n".join(lines), "\n".join(sources)


def write_umbrella(rows: list[dict]) -> None:
    dist = "pyd3"
    pkg_dir = ROOT / "packages" / dist
    imp = "pyd3"
    src = pkg_dir / "src" / imp
    src.mkdir(parents=True, exist_ok=True)
    deps = [r["dist"] for r in rows]
    dep_lines_list = [f'    "{d}>=0.0.0",' for d in deps]
    src_lines = [f"{d} = {{ workspace = true }}" for d in deps]
    (pkg_dir / "pyproject.toml").write_text(
        f"""[project]
name = "pyd3"
version = "0.0.0"
description = "Python port of the D3 bundle (metapackage)"
requires-python = ">=3.10"
readme = "README.md"
authors = [{{ name = "pyd3 contributors" }}]
dependencies = [
{chr(10).join(dep_lines_list)}
]

[build-system]
requires = ["hatchling>=1.18.0"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/pyd3"]

[tool.uv.sources]
{chr(10).join(src_lines)}
"""
    )
    (pkg_dir / "README.md").write_text(
        """# pyd3

Umbrella package re-exporting all `pyd3js-*` modules (Python port of [d3](https://github.com/d3/d3)).
"""
    )
    init = src / "__init__.py"
    if not init.exists():
        init.write_text(
            '"""D3 in Python — umbrella re-exports."""\n\n__version__ = "0.0.0"\n'
        )


def main() -> None:
    rows = json.loads(MANIFEST.read_text())
    for row in rows:
        dist = row["dist"]
        imp = row["import"]
        npm = dist.replace("pyd3js-", "d3-", 1) if dist != "pyd3" else "d3"
        pkg_dir = ROOT / "packages" / dist
        src = pkg_dir / "src" / imp
        src.mkdir(parents=True, exist_ok=True)
        deps_body, uv_src = dep_lines(row.get("deps", []))
        uv_block = "\n[tool.uv.sources]\n" + uv_src + "\n" if uv_src else ""
        pyproject = PYPROJECT_TEMPLATE.format(
            dist=dist,
            npm_name=npm,
            import_name=imp,
            deps_lines=deps_body,
            uv_sources_block=uv_block,
        )
        (pkg_dir / "pyproject.toml").write_text(pyproject)
        (pkg_dir / "README.md").write_text(
            README_TEMPLATE.format(dist=dist, npm_name=npm)
        )
        init_py = pkg_dir / "src" / imp / "__init__.py"
        if not init_py.exists():
            init_py.write_text(INIT_TEMPLATE.format(pydist=dist, npm_name=npm))
    write_umbrella(rows)


if __name__ == "__main__":
    main()
