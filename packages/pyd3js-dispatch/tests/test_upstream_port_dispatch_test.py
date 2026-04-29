from __future__ import annotations

from typing import Any, cast

import pytest

from pyd3js_dispatch import dispatch
from pyd3js_dispatch.dispatch import Dispatch


class _Str:
    def __init__(self, s: str) -> None:
        self._s = s

    def __str__(self) -> str:  # pragma: no cover
        return self._s


def test_upstream_dispatch_returns_dispatch_object_with_types() -> None:
    d = dispatch("foo", "bar")
    assert isinstance(d, Dispatch)


def test_upstream_dispatch_allows_type_name_collision_with_method() -> None:
    d = dispatch("on")
    assert isinstance(d, Dispatch)


def test_upstream_dispatch_throws_if_type_name_is_illegal() -> None:
    with pytest.raises(ValueError):
        dispatch("__proto__")
    with pytest.raises(ValueError):
        dispatch("hasOwnProperty")
    with pytest.raises(ValueError):
        dispatch("")
    with pytest.raises(ValueError):
        dispatch("foo.bar")
    with pytest.raises(ValueError):
        dispatch("foo bar")
    with pytest.raises(ValueError):
        dispatch("foo\tbar")


def test_upstream_dispatch_throws_if_type_name_is_duplicate() -> None:
    with pytest.raises(ValueError):
        dispatch("foo", "foo")


def test_upstream_call_invokes_callbacks_of_specified_type() -> None:
    foo = 0
    bar = 0

    def on_foo(_this) -> None:
        nonlocal foo
        foo += 1

    def on_bar(_this) -> None:
        nonlocal bar
        bar += 1

    d = dispatch("foo", "bar").on("foo", on_foo).on("bar", on_bar)
    d.call("foo")
    assert foo == 1
    assert bar == 0
    d.call("foo")
    d.call("bar")
    assert foo == 2
    assert bar == 1


def test_upstream_call_invokes_with_args_and_context() -> None:
    results: list[dict[str, object]] = []
    foo = object()
    bar = object()

    def cb(this, *args) -> None:
        results.append({"this": this, "arguments": list(args)})

    d = dispatch("foo").on("foo", cb)
    d.call("foo", foo, bar)
    assert results == [{"this": foo, "arguments": [bar]}]
    d.call("foo", bar, foo, 42, "baz")
    assert results == [
        {"this": foo, "arguments": [bar]},
        {"this": bar, "arguments": [foo, 42, "baz"]},
    ]


def test_upstream_call_order_is_add_order_and_replacing_moves_to_end() -> None:
    results: list[str] = []
    d = dispatch("foo")
    d.on("foo.a", lambda *_: results.append("A"))
    d.on("foo.b", lambda *_: results.append("B"))
    d.call("foo")
    d.on("foo.c", lambda *_: results.append("C"))
    d.on("foo.a", lambda *_: results.append("A"))  # move to end
    d.call("foo")
    assert results == ["A", "B", "B", "C", "A"]


def test_upstream_call_returns_undefined() -> None:
    d = dispatch("foo")
    assert d.call("foo") is None


def test_upstream_apply_invokes_callbacks_of_specified_type() -> None:
    foo = 0
    bar = 0

    def on_foo(_this) -> None:
        nonlocal foo
        foo += 1

    def on_bar(_this) -> None:
        nonlocal bar
        bar += 1

    d = dispatch("foo", "bar").on("foo", on_foo).on("bar", on_bar)
    d.apply("foo")
    assert foo == 1
    assert bar == 0
    d.apply("foo")
    d.apply("bar")
    assert foo == 2
    assert bar == 1


def test_upstream_apply_invokes_with_args_and_context() -> None:
    results: list[dict[str, object]] = []
    foo = object()
    bar = object()

    def cb(this, *args) -> None:
        results.append({"this": this, "arguments": list(args)})

    d = dispatch("foo").on("foo", cb)
    d.apply("foo", foo, [bar])
    assert results == [{"this": foo, "arguments": [bar]}]
    d.apply("foo", bar, [foo, 42, "baz"])
    assert results == [
        {"this": foo, "arguments": [bar]},
        {"this": bar, "arguments": [foo, 42, "baz"]},
    ]


def test_upstream_apply_order_is_add_order_and_replacing_moves_to_end() -> None:
    results: list[str] = []
    d = dispatch("foo")
    d.on("foo.a", lambda *_: results.append("A"))
    d.on("foo.b", lambda *_: results.append("B"))
    d.apply("foo")
    d.on("foo.c", lambda *_: results.append("C"))
    d.on("foo.a", lambda *_: results.append("A"))  # move to end
    d.apply("foo")
    assert results == ["A", "B", "B", "C", "A"]


def test_upstream_apply_returns_undefined() -> None:
    d = dispatch("foo")
    assert d.apply("foo") is None


def test_upstream_on_returns_dispatch_object() -> None:
    d = dispatch("foo")
    assert d.on("foo", lambda *_: None) is d


def test_upstream_on_replaces_existing_callback() -> None:
    foo = 0
    bar = 0
    d = dispatch("foo", "bar")

    # Use explicit funcs to avoid weird closure on mypy/locals().
    def a(_this) -> None:
        nonlocal foo
        foo += 1

    def b(_this) -> None:
        nonlocal bar
        bar += 1

    d.on("foo", a)
    d.call("foo")
    assert foo == 1
    assert bar == 0
    d.on("foo", b)
    d.call("foo")
    assert foo == 1
    assert bar == 1


def test_upstream_on_replacing_existing_with_itself_has_no_effect() -> None:
    foo = 0

    def FOO(_this) -> None:
        nonlocal foo
        foo += 1

    d = dispatch("foo").on("foo", FOO)
    d.call("foo")
    assert foo == 1
    d.on("foo", FOO).on("foo", FOO).on("foo", FOO)
    d.call("foo")
    assert foo == 2


def test_upstream_on_type_dot_equivalent_to_type() -> None:
    d = dispatch("foo")
    foos = 0
    bars = 0

    def foo(_this) -> None:
        nonlocal foos
        foos += 1

    def bar(_this) -> None:
        nonlocal bars
        bars += 1

    assert d.on("foo.", foo) is d
    assert d.on("foo.") is foo
    assert d.on("foo") is foo
    assert d.on("foo.", bar) is d
    assert d.on("foo.") is bar
    assert d.on("foo") is bar
    assert d.call("foo") is None
    assert foos == 0
    assert bars == 1
    assert d.on(".", None) is d
    assert d.on("foo") is None
    assert d.call("foo") is None
    assert foos == 0
    assert bars == 1


def test_upstream_on_null_removes_existing_callback() -> None:
    foo = 0
    d = dispatch("foo", "bar")

    def inc(_this) -> None:
        nonlocal foo
        foo += 1

    d.on("foo", inc)
    d.call("foo")
    assert foo == 1
    d.on("foo", None)
    d.call("foo")
    assert foo == 1


def test_upstream_on_null_does_not_remove_shared_callback() -> None:
    a = 0

    def A(_this) -> None:
        nonlocal a
        a += 1

    d = dispatch("foo", "bar").on("foo", A).on("bar", A)
    d.call("foo")
    d.call("bar")
    assert a == 2
    d.on("foo", None)
    d.call("bar")
    assert a == 3


def test_upstream_on_null_removing_missing_callback_has_no_effect() -> None:
    a = 0
    d = dispatch("foo")

    def A(_this) -> None:
        nonlocal a
        a += 1

    d.on("foo.a", None).on("foo", A).on("foo", None).on("foo", None)
    d.call("foo")
    assert a == 0


def test_upstream_on_null_during_callback_does_not_invoke_old_callback() -> None:
    a = 0
    b = 0

    d = dispatch("foo")

    def A(_this) -> None:
        nonlocal a
        a += 1
        d.on("foo.B", None)  # remove B

    def B(_this) -> None:
        nonlocal b
        b += 1

    d.on("foo.A", A).on("foo.B", B)
    d.call("foo")
    assert a == 1
    assert b == 0


def test_upstream_on_replace_during_callback_does_not_invoke_old_or_new() -> None:
    a = 0
    b = 0
    c = 0

    d = dispatch("foo")

    def A(_this) -> None:
        nonlocal a
        a += 1
        d.on("foo.B", C)  # replace B with C

    def B(_this) -> None:
        nonlocal b
        b += 1

    def C(_this) -> None:
        nonlocal c
        c += 1

    d.on("foo.A", A).on("foo.B", B)
    d.call("foo")
    assert a == 1
    assert b == 0
    assert c == 0


def test_upstream_on_add_during_callback_does_not_invoke_new_callback() -> None:
    a = 0
    b = 0
    d = dispatch("foo")

    def A(_this) -> None:
        nonlocal a
        a += 1
        d.on("foo.B", B)  # add B

    def B(_this) -> None:
        nonlocal b
        b += 1

    d.on("foo.A", A)
    d.call("foo")
    assert a == 1
    assert b == 0


def test_upstream_on_coerces_type_to_string() -> None:
    def f(*_args) -> None:
        return None

    def g(*_args) -> None:
        return None

    nullish = _Str("null")
    undefish = _Str("undefined")
    d = dispatch(nullish, undefish).on(nullish, f).on(undefish, g)
    assert d.on(nullish) is f
    assert d.on(undefish) is g


def test_upstream_on_foo_bar_adds_callback_for_both_types() -> None:
    foos = 0

    def foo(_this) -> None:
        nonlocal foos
        foos += 1

    d = dispatch("foo", "bar").on("foo bar", foo)
    assert d.on("foo") is foo
    assert d.on("bar") is foo
    d.call("foo")
    assert foos == 1
    d.call("bar")
    assert foos == 2


def test_upstream_on_two_typenames_adds_callback_for_both() -> None:
    foos = 0

    def foo(_this) -> None:
        nonlocal foos
        foos += 1

    d = dispatch("foo").on("foo.one foo.two", foo)
    assert d.on("foo.one") is foo
    assert d.on("foo.two") is foo
    d.call("foo")
    assert foos == 2


def test_upstream_on_two_types_get_returns_callback_for_either_type() -> None:
    def foo(*_args) -> None:
        return None

    d = dispatch("foo", "bar")
    d.on("foo", foo)
    assert d.on("foo bar") is foo
    assert d.on("bar foo") is foo
    d.on("foo", None).on("bar", foo)
    assert d.on("foo bar") is foo
    assert d.on("bar foo") is foo


def test_upstream_on_two_typenames_get_returns_callback_for_either_typename() -> None:
    def foo(*_args) -> None:
        return None

    d = dispatch("foo")
    d.on("foo.one", foo)
    assert d.on("foo.one foo.two") is foo
    assert d.on("foo.two foo.one") is foo
    assert d.on("foo foo.one") is foo
    assert d.on("foo.one foo") is foo
    d.on("foo.one", None).on("foo.two", foo)
    assert d.on("foo.one foo.two") is foo
    assert d.on("foo.two foo.one") is foo
    assert d.on("foo foo.two") is foo
    assert d.on("foo.two foo") is foo


def test_upstream_on_remove_multiple_namespaced_callbacks() -> None:
    def foo(*_args) -> None:
        return None

    d = dispatch("foo")
    d.on("foo.one", foo)
    d.on("foo.two", foo)
    d.on("foo.one foo.two", None)
    assert d.on("foo.one") is None
    assert d.on("foo.two") is None


def test_upstream_on_throws_if_callback_not_function() -> None:
    with pytest.raises(ValueError):
        dispatch("foo").on("foo", cast(Any, 42))


def test_upstream_on_throws_if_type_unknown_when_setting() -> None:
    with pytest.raises(ValueError):
        dispatch("foo").on("bar", lambda *_: None)
    with pytest.raises(ValueError):
        dispatch("foo").on("__proto__", lambda *_: None)


def test_upstream_on_throws_if_type_unknown_when_getting() -> None:
    with pytest.raises(ValueError):
        dispatch("foo").on("bar")
    with pytest.raises(ValueError):
        dispatch("foo").on("__proto__")


def test_upstream_on_get_returns_expected_callback() -> None:
    d = dispatch("foo")

    def A(_this) -> None: ...

    def B(_this) -> None: ...

    def C(_this) -> None: ...

    d.on("foo.a", A).on("foo.b", B).on("foo", C)
    assert d.on("foo.a") is A
    assert d.on("foo.b") is B
    assert d.on("foo") is C


def test_upstream_on_dot_name_get_returns_undefined() -> None:
    d = dispatch("foo").on("foo.a", lambda *_: None)
    assert d.on(".a") is None


def test_upstream_on_dot_name_null_removes_callbacks_with_name() -> None:
    d = dispatch("foo", "bar")
    those: list[object] = []
    a = object()
    b = object()
    c = object()

    def A(_this) -> None:
        those.append(a)

    def B(_this) -> None:
        those.append(b)

    def C(_this) -> None:
        those.append(c)

    d.on("foo.a", A).on("bar.a", B).on("foo", C).on(".a", None)
    d.call("foo")
    d.call("bar")
    assert those == [c]


def test_upstream_on_dot_name_set_has_no_effect() -> None:
    d = dispatch("foo", "bar")
    those: list[object] = []
    a = object()
    b = object()

    def A(_this) -> None:
        those.append(a)

    def B(_this) -> None:
        those.append(b)

    d.on(".a", A).on("foo.a", B).on("bar", B)
    d.call("foo")
    d.call("bar")
    assert those == [b, b]
    assert d.on(".a") is None


def test_upstream_copy_returns_isolated_copy() -> None:
    def foo(*_args) -> None:
        return None

    def bar(*_args) -> None:
        return None

    d0 = dispatch("foo", "bar").on("foo", foo).on("bar", bar)
    d1 = d0.copy()
    assert d1.on("foo") is foo
    assert d1.on("bar") is bar

    # Changes to d1 don’t affect d0.
    assert d1.on("bar", None) is d1
    assert d1.on("bar") is None
    assert d0.on("bar") is bar

    # Changes to d0 don’t affect d1.
    assert d0.on("foo", None) is d0
    assert d0.on("foo") is None
    assert d1.on("foo") is foo
