from pyd3js_path import Path, path, pathRound


def test_full_coverage_smoke() -> None:
    # Drive remaining branches lightly.
    p = Path()
    p.closePath()  # empty no-op
    p.arcTo(1, 2, 3, 4, 0)  # empty path -> moveTo
    p.moveTo(1, 2)
    p.arcTo(1, 2, 3, 4, 10)  # previous point coincident -> no-op
    p.moveTo(0, 0)
    p.arc(0, 0, 0, 0, 0)  # radius zero
    p.arc(0, 0, 10, 0, -1e-3, True)  # da negative, ccw -> normalize

    p2 = pathRound(0)
    p2.rect(0.4, 0.6, 0.9, 1.1)

    assert isinstance(path(), Path)
    assert repr(Path()) == "Path('')"
