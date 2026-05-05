"""Schedule dict lives on ``__transition__`` or legacy ``__transition``."""

from __future__ import annotations

from pyd3js_transition._schedules import schedules_get, schedules_try_del


def test_schedules_get_prefers_dunder_then_single() -> None:
    class N:
        pass

    n = N()
    n.__transition = {"1": {"state": 0}}
    assert schedules_get(n) == {"1": {"state": 0}}

    n.__transition__ = {"2": {"state": 1}}
    assert schedules_get(n) == {"2": {"state": 1}}


def test_schedules_try_del_removes_either_attr() -> None:
    class N:
        pass

    a = N()
    a.__transition__ = {}
    schedules_try_del(a)
    assert not hasattr(a, "__transition__")

    b = N()
    b.__transition = {}
    schedules_try_del(b)
    assert not hasattr(b, "__transition")
