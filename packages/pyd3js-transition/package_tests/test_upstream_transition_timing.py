from __future__ import annotations

import pytest

import pyd3js_selection._globals as g
from pyd3js_ease import easeBounce, easePolyIn
from pyd3js_selection._dom import Document, parse_html
from pyd3js_selection.select import select
from pyd3js_selection.selectAll import selectAll
import pyd3js_timer._engine as timer_engine
import pyd3js_transition  # noqa: F401  (patches selection)
from pyd3js_transition.transition import schedule as sched


def _with_virtual_time() -> callable:
    wall = [0.0]
    timer_engine._set_wall_ms_factory(lambda: wall[0])
    timer_engine._reset_for_tests()

    def step(ms: float) -> None:
        wall[0] += ms
        timer_engine._clear_now()
        timer_engine.timer_flush()
        timer_engine.timer_flush()

    return step


def _set_two_div_document() -> None:
    g.document = parse_html(
        """
        <html>
          <body>
            <div id="one"></div>
            <div id="two"></div>
          </body>
        </html>
        """
    )


def _set_two_h1_document() -> None:
    # easeVarying upstream uses document + two h1s.
    g.document = parse_html(
        """
        <html>
          <body>
            <h1 id="one"></h1>
            <h1 id="two"></h1>
          </body>
        </html>
        """
    )


def test_transition_delay_getter_and_reselect() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t1 = select(one).transition()
    t2 = select(two).transition().delay(50)
    assert one.__transition__[t1._id]["delay"] == 0
    assert two.__transition__[t2._id]["delay"] == 50
    assert t1.delay() == 0
    assert t2.delay() == 50
    assert select(one).transition(t1).delay() == 0
    assert select(two).transition(t2).delay() == 50
    assert selectAll([None, one]).transition(t1).delay() == 0
    assert selectAll([None, two]).transition(t2).delay() == 50


def test_transition_delay_number_sets_delay() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().delay(50)
    assert one.__transition__[t._id]["delay"] == 50
    assert two.__transition__[t._id]["delay"] == 50


def test_transition_delay_coerces_to_number() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().delay("50")
    assert one.__transition__[t._id]["delay"] == 50
    assert two.__transition__[t._id]["delay"] == 50


def test_transition_delay_function_args_and_context() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    result: list[object] = []
    s = selectAll([one, two]).data(["one", "two"])

    def f(d, i, nodes):  # noqa: ANN001
        result.append([d, i, nodes, self])  # type: ignore[name-defined]

    # Bind `this` like D3: our _call_value passes `this` as first arg, so define as method-like.
    def delay_fn(this, d, i, nodes):  # noqa: ANN001
        result.append([d, i, nodes, this])

    t = s.transition().delay(delay_fn)
    assert result == [
        ["one", 0, t._groups[0], one],
        ["two", 1, t._groups[0], two],
    ]


def test_transition_delay_function_sets_per_node_values() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().delay(lambda _d, i, _n=None: i * 20)
    assert one.__transition__[t._id]["delay"] == 0
    assert two.__transition__[t._id]["delay"] == 20


def test_transition_delay_function_return_is_coerced_to_number() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().delay(lambda _d, i, _n=None: f"{i * 20}")
    assert one.__transition__[t._id]["delay"] == 0
    assert two.__transition__[t._id]["delay"] == 20


def test_transition_duration_getter_and_reselect() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t1 = select(one).transition()
    t2 = select(two).transition().duration(50)
    assert one.__transition__[t1._id]["duration"] == 250
    assert two.__transition__[t2._id]["duration"] == 50
    assert t1.duration() == 250
    assert t2.duration() == 50
    assert select(one).transition(t1).duration() == 250
    assert select(two).transition(t2).duration() == 50
    assert selectAll([None, one]).transition(t1).duration() == 250
    assert selectAll([None, two]).transition(t2).duration() == 50


def test_transition_duration_number_sets_duration() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().duration(50)
    assert one.__transition__[t._id]["duration"] == 50
    assert two.__transition__[t._id]["duration"] == 50


def test_transition_duration_coerces_to_number() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().duration("50")
    assert one.__transition__[t._id]["duration"] == 50
    assert two.__transition__[t._id]["duration"] == 50


def test_transition_duration_function_args_and_context() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    results: list[object] = []
    s = selectAll([one, two]).data(["one", "two"])

    def duration_fn(this, d, i, nodes):  # noqa: ANN001
        results.append([d, i, nodes, this])

    t = s.transition().duration(duration_fn)
    assert results == [
        ["one", 0, t._groups[0], one],
        ["two", 1, t._groups[0], two],
    ]


def test_transition_duration_function_sets_per_node_values() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().duration(lambda _d, i, _n=None: i * 20)
    assert one.__transition__[t._id]["duration"] == 0
    assert two.__transition__[t._id]["duration"] == 20


def test_transition_duration_function_return_is_coerced_to_number() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().duration(lambda _d, i, _n=None: f"{i * 20}")
    assert one.__transition__[t._id]["duration"] == 0
    assert two.__transition__[t._id]["duration"] == 20


def test_transition_ease_getter_and_reselect() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t1 = select(one).transition()
    t2 = select(two).transition().ease(easeBounce)
    assert one.__transition__[t1._id]["ease"] is not None
    assert two.__transition__[t2._id]["ease"] is easeBounce
    assert t2.ease() is easeBounce
    assert select(two).transition(t2).ease() is easeBounce
    assert selectAll([None, two]).transition(t2).ease() is easeBounce


def test_transition_ease_raises_if_not_callable() -> None:
    _set_two_div_document()
    root = g.document.documentElement
    t = select(root).transition()
    with pytest.raises(Exception):
        t.ease(42)  # type: ignore[arg-type]
    with pytest.raises(Exception):
        t.ease(None)  # type: ignore[arg-type]


def test_transition_ease_sets_function_for_each_selected_element() -> None:
    _set_two_div_document()
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None
    t = selectAll([one, two]).transition().ease(easeBounce)
    assert one.__transition__[t._id]["ease"] is easeBounce
    assert two.__transition__[t._id]["ease"] is easeBounce


def test_transition_ease_passes_normalized_time_and_skips_last_frame() -> None:
    _set_two_div_document()
    step = _with_virtual_time()
    root = g.document.documentElement

    seen: list[float] = []

    def ease(x: float) -> float:
        seen.append(x)
        return x

    t = select(root).transition().ease(ease)
    schedule = root.__transition__[t._id]

    step(0)  # start + first tick
    step(100)  # mid tick (100/250)
    assert any(abs(v - 0.4) < 1e-9 for v in seen)

    n_before_end = len(seen)
    step(200)  # crosses end; final frame should not call ease again
    assert schedule["state"] == sched.ENDED
    assert len(seen) == n_before_end


def test_transition_ease_observes_eased_time_returned_by_function() -> None:
    _set_two_div_document()
    step = _with_virtual_time()
    root = g.document.documentElement

    expected = {"v": 0.0}

    def ease(_x: float) -> float:
        expected["v"] = -0.25
        return expected["v"]

    def tween_value(*_args):
        def tick(_node, tt: float) -> None:
            schedule = root.__transition__[t._id]
            if schedule["state"] == sched.ENDING:
                assert tt == 1.0
            else:
                assert tt == expected["v"]

        return tick

    t = select(root).transition().ease(ease).tween("tween", tween_value)
    step(0)
    step(300)


def test_transition_ease_varying_accepts_factory() -> None:
    _set_two_h1_document()
    t = select(g.document).selectAll("h1").data([{"exponent": 3}, {"exponent": 4}]).transition()
    t.easeVarying(lambda d, *_: easePolyIn.exponent(d["exponent"]))
    assert t.ease()(0.5) == easePolyIn.exponent(3)(0.5)


def test_transition_ease_varying_passes_expected_args_and_this() -> None:
    _set_two_h1_document()
    t = select(g.document).selectAll("h1").data([{"exponent": 3}, {"exponent": 4}]).transition()
    results: list[list[object]] = []
    one = g.document.querySelector("#one")
    two = g.document.querySelector("#two")
    assert one is not None and two is not None

    def factory(this, d, i, e):  # noqa: ANN001
        results.append([d, i, e, this])
        return lambda x: x

    t.easeVarying(factory)
    assert results == [
        [{"exponent": 3}, 0, list(t), one],
        [{"exponent": 4}, 1, list(t), two],
    ]


def test_transition_ease_varying_raises_if_not_callable() -> None:
    _set_two_h1_document()
    t = select(g.document).selectAll("h1").data([{"exponent": 3}, {"exponent": 4}]).transition()
    with pytest.raises(Exception):
        t.easeVarying()  # type: ignore[call-arg]
    with pytest.raises(Exception):
        t.easeVarying("a")  # type: ignore[arg-type]

