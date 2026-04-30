from __future__ import annotations

from pyd3js_dispatch import dispatch


def test_call_passes_that_and_args() -> None:
    d = dispatch("t")
    seen: list[tuple[object, tuple[object, ...]]] = []
    that = object()

    d.on("t.ns", lambda this, *args: seen.append((this, args)))
    d.call("t", that, 1, "x", None)

    assert seen == [(that, (1, "x", None))]


def test_apply_passes_that_and_args_list() -> None:
    d = dispatch("t")
    seen: list[tuple[object, tuple[object, ...]]] = []
    that = object()

    d.on("t.ns", lambda this, *args: seen.append((this, args)))
    d.apply("t", that, [1, "x", None])

    assert seen == [(that, (1, "x", None))]


def test_call_and_apply_run_all_listeners() -> None:
    d = dispatch("t")
    log: list[str] = []

    d.on("t.a", lambda *_: log.append("a"))
    d.on("t.b", lambda *_: log.append("b"))
    d.call("t", None)
    d.apply("t", None, [])

    assert log == ["a", "b", "a", "b"]
