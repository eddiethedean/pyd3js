from pyd3js_path import Path, path, pathRound


def test_public_exports_are_present() -> None:
    # Minimal gate: if upstream adds/removes exports, update docs + __all__ + this list.
    assert Path is not None
    assert path is not None
    assert pathRound is not None
