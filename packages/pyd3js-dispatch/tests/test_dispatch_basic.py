from __future__ import annotations

from pyd3js_dispatch import dispatch


def test_dispatch_on_and_call() -> None:
    d = dispatch("start", "end")
    log: list[object] = []

    d.on("start.foo", lambda this, x: log.append(("foo", x)))
    d.call("start", None, 1)
    assert log == [("foo", 1)]

    d.on("start.foo", None)
    d.call("start", None, 2)
    assert log == [("foo", 1)]


def test_dispatch_copy_isolation() -> None:
    d = dispatch("t")
    d.on("t.a", lambda *_: None)
    c = d.copy()
    c.on("t.a", None)
    assert d.on("t.a") is not None
    assert c.on("t.a") is None
