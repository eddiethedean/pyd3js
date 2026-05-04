from __future__ import annotations

import time

import pytest

import pyd3js_transition as dt
from pyd3js_selection.selection.index import selection


class Node:
    def __init__(self) -> None:
        self.__data__ = None
        self.attrs: dict[str, str] = {}
        self.style: dict[str, str] = {}
        self.textContent = ""
        self.parentNode = None

    def getAttribute(self, name: str) -> str | None:  # noqa: N802
        return self.attrs.get(name)

    def setAttribute(self, name: str, value: str) -> None:  # noqa: N802
        self.attrs[name] = value

    def removeAttribute(self, name: str) -> None:  # noqa: N802
        self.attrs.pop(name, None)


class Parent:
    def __init__(self) -> None:
        self.children: list[Node] = []

    def removeChild(self, child: Node) -> None:  # noqa: N802
        self.children = [c for c in self.children if c is not child]


def test_transition_export_surface() -> None:
    assert callable(dt.transition)
    assert callable(dt.active)
    assert callable(dt.interrupt)
    assert hasattr(dt, "Transition")


def test_selection_transition_creates_transition_and_schedule() -> None:
    n = Node()
    s = selection([[n]], [None])
    t = s.transition("x")
    assert isinstance(t, dt.Transition)
    assert getattr(n, "__transition__", None) is not None


def test_attr_style_text_tweens_apply() -> None:
    n = Node()
    s = selection([[n]], [None])

    done = []

    def on_end(_this, *_args):  # noqa: ANN001
        done.append(True)

    t = s.transition("a").duration(30).attr("x", 10).style("fill", "red").text("hi").on("end.test", on_end)

    # Wait for the transition to finish.
    deadline = time.monotonic() + 2.0
    while not done and time.monotonic() < deadline:
        time.sleep(0.01)

    assert done
    assert n.getAttribute("x") == "10"
    assert n.style["fill"] == "red"
    assert n.textContent == "hi"


def test_end_future_resolves() -> None:
    n = Node()
    s = selection([[n]], [None])
    fut = s.transition("f").duration(10).end()
    assert fut.result(timeout=2.0) is None


def test_interrupt_cancels_end_future() -> None:
    n = Node()
    s = selection([[n]], [None])
    t = s.transition("i").duration(200)
    fut = t.end()
    dt.interrupt(n, "i")
    with pytest.raises(Exception):
        fut.result(timeout=2.0)


def test_remove_on_end() -> None:
    p = Parent()
    n = Node()
    n.parentNode = p
    p.children.append(n)
    s = selection([[n]], [None])
    s.transition("r").duration(10).remove().end().result(timeout=2.0)
    assert n not in p.children

