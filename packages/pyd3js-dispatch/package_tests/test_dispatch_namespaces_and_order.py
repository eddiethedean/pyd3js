from __future__ import annotations

from pyd3js_dispatch import dispatch


def test_listener_invocation_order_is_insertion_order() -> None:
    d = dispatch("t")
    log: list[str] = []

    d.on("t.a", lambda *_: log.append("a"))
    d.on("t.b", lambda *_: log.append("b"))
    d.call("t", None)

    assert log == ["a", "b"]


def test_setting_same_namespace_replaces_previous_listener() -> None:
    d = dispatch("t")
    log: list[str] = []

    d.on("t.ns", lambda *_: log.append("first"))
    d.on("t.ns", lambda *_: log.append("second"))
    d.call("t", None)

    assert log == ["second"]


def test_remove_by_namespaced_typename() -> None:
    d = dispatch("t")
    log: list[str] = []

    d.on("t.keep", lambda *_: log.append("keep"))
    d.on("t.rm", lambda *_: log.append("rm"))
    d.on("t.rm", None)
    d.call("t", None)

    assert log == ["keep"]


def test_remove_across_all_types_with_dot_namespace() -> None:
    d = dispatch("a", "b")
    log: list[str] = []

    d.on("a.ns", lambda *_: log.append("a"))
    d.on("b.ns", lambda *_: log.append("b"))
    d.on(".ns", None)

    d.call("a", None)
    d.call("b", None)
    assert log == []


def test_dot_namespace_set_is_noop_in_python_port() -> None:
    # Mirrors d3-dispatch behavior: setting with no explicit type is ignored unless
    # used to remove (callback=None).
    d = dispatch("a")
    log: list[str] = []

    d.on(".ns", lambda *_: log.append("x"))
    d.call("a", None)

    assert log == []
