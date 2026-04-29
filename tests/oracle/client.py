from __future__ import annotations

import hashlib
import json
import math
import os
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
ORACLE_JS = ROOT / "tools" / "oracle" / "run.mjs"
CACHE_DIR = ROOT / "tests" / "_oracle_cache"


def oracle_available() -> bool:
    return ORACLE_JS.is_file() and (ROOT / "tools" / "oracle" / "node_modules").is_dir()


def _decode_jsonish(x: Any) -> Any:
    if isinstance(x, dict):
        if x.get("__nan__"):
            return float("nan")
        if x.get("__undefined__"):
            return None
        if "__date__" in x:
            from datetime import datetime

            return datetime.fromisoformat(x["__date__"].replace("Z", "+00:00"))
        return {k: _decode_jsonish(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_decode_jsonish(v) for v in x]
    return x


def oracle_eval(expr: str, *, use_cache: bool | None = None) -> Any:
    if use_cache is None:
        use_cache = os.environ.get("ORACLE_CACHE", "1") not in ("0", "false", "")

    if not oracle_available():
        raise RuntimeError(
            "Oracle not available: run `npm install` in tools/oracle"
        )

    payload = json.dumps({"op": "eval", "expr": expr}, separators=(",", ":"))
    key = hashlib.sha256(payload.encode()).hexdigest()
    cache_path = CACHE_DIR / f"{key}.json"
    if use_cache and cache_path.is_file():
        return _decode_jsonish(json.loads(cache_path.read_text()))

    proc = subprocess.run(
        ["node", str(ORACLE_JS)],
        input=payload,
        capture_output=True,
        text=True,
        cwd=str(ROOT / "tools" / "oracle"),
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or proc.stdout or "oracle failed")
    out = json.loads(proc.stdout)
    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(out))
    return _decode_jsonish(out)


def assert_approx_oracle(py_val: Any, expr: str, *, rel: float = 1e-12, abs: float = 1e-12) -> None:
    expected = oracle_eval(expr)
    if isinstance(py_val, float) and isinstance(expected, float):
        if math.isnan(py_val) and math.isnan(expected):
            return
    assert py_val == expected or (
        isinstance(py_val, (int, float))
        and isinstance(expected, (int, float))
        and math.isclose(py_val, expected, rel_tol=rel, abs_tol=abs)
    ), (py_val, expected)
