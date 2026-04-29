from __future__ import annotations

import pytest

from pyd3js_dispatch import dispatch


class Strish:
    def __init__(self, s: str) -> None:
        self._s = s

    def __str__(self) -> str:
        return self._s


def test_dispatch_coerces_typenames_to_string() -> None:
    d = dispatch(Strish("foo"), Strish("bar"))
    log: list[str] = []
    d.on("foo.ns", lambda *_: log.append("foo"))
    d.on("bar.ns", lambda *_: log.append("bar"))
    d.call("foo")
    d.call("bar")
    assert log == ["foo", "bar"]


def test_on_coerces_typename_to_string() -> None:
    d = dispatch("foo")
    log: list[str] = []
    d.on(Strish("foo.ns"), lambda *_: log.append("x"))
    d.call("foo")
    assert log == ["x"]


def test_call_default_that_is_none() -> None:
    d = dispatch("t")
    seen: list[object] = []
    d.on("t.ns", lambda this: seen.append(this))
    d.call("t")
    assert seen == [None]


def test_apply_default_args_is_empty_list() -> None:
    d = dispatch("t")
    seen: list[tuple[object, tuple[object, ...]]] = []
    d.on("t.ns", lambda this, *args: seen.append((this, args)))
    d.apply("t", object())
    assert len(seen) == 1
    assert seen[0][1] == ()


def test_callback_exceptions_propagate_and_stop_iteration() -> None:
    d = dispatch("t")
    log: list[str] = []

    def boom(_this) -> None:
        raise RuntimeError("boom")

    d.on("t.a", lambda *_: log.append("a"))
    d.on("t.b", boom)
    d.on("t.c", lambda *_: log.append("c"))

    with pytest.raises(RuntimeError, match="boom"):
        d.call("t")

    # "c" should not run after the exception.
    assert log == ["a"]


def test_on_with_empty_string_is_type_error_like_upstream_unknown_type() -> None:
    # Upstream parseTypenames trims and splits; empty/whitespace results in no entries.
    # In our port, empty string returns no entries too; setting should be a no-op.
    d = dispatch("t")
    assert d.on("", None) is d
    assert d.on("   ", None) is d

