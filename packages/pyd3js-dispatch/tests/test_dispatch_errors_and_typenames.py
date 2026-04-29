from __future__ import annotations

from typing import Any, cast

import pytest

from pyd3js_dispatch import dispatch


def test_dispatch_illegal_typenames() -> None:
    with pytest.raises(ValueError, match=r"illegal type"):
        dispatch("")
    with pytest.raises(ValueError, match=r"illegal type"):
        dispatch(" ")
    with pytest.raises(ValueError, match=r"illegal type"):
        dispatch("a b")
    with pytest.raises(ValueError, match=r"illegal type"):
        dispatch(".")
    with pytest.raises(ValueError, match=r"illegal type"):
        dispatch("a.b")


def test_dispatch_duplicate_typename() -> None:
    with pytest.raises(ValueError, match=r"illegal type"):
        dispatch("a", "a")


def test_on_invalid_callback() -> None:
    d = dispatch("t")
    with pytest.raises(ValueError, match=r"invalid callback"):
        d.on("t.ns", cast(Any, object()))


def test_on_unknown_type_rejected() -> None:
    d = dispatch("known")
    with pytest.raises(ValueError, match=r"unknown type"):
        d.on("unknown", lambda *_: None)


def test_call_unknown_type_rejected() -> None:
    d = dispatch("known")
    with pytest.raises(ValueError, match=r"unknown type"):
        d.call("unknown", None)


def test_apply_unknown_type_rejected() -> None:
    d = dispatch("known")
    with pytest.raises(ValueError, match=r"unknown type"):
        d.apply("unknown", None, [])


def test_on_get_returns_none_when_not_set() -> None:
    d = dispatch("t")
    assert d.on("t.ns") is None


def test_on_whitespace_typename_is_ignored_for_get() -> None:
    d = dispatch("t")
    assert d.on("   ") is None


def test_on_multiple_typenames_get_prefers_first_found() -> None:
    d = dispatch("a", "b")
    d.on("b.ns", lambda *_: "from-b")
    cb1 = d.on("a.ns b.ns")
    assert cb1 is not None
    assert cb1() == "from-b"
    d.on("a.ns", lambda *_: "from-a")
    cb2 = d.on("a.ns b.ns")
    assert cb2 is not None
    assert cb2() == "from-a"
