"""Port of d3-timer ``test/timerFlush-test.js``."""

from __future__ import annotations

from pyd3js_timer import now, timer, timer_flush


def test_timer_flush_immediately_invokes_eligible_timers() -> None:
    count = [0]

    def cb(_e: float) -> None:
        count[0] += 1
        t_holder[0].stop()

    t_holder: list = [timer(cb)]
    timer_flush()
    timer_flush()
    assert count[0] == 1


def test_timer_flush_nested_still_executes_all_eligible() -> None:
    count = [0]
    t_holder: list = []

    def cb(_e: float) -> None:
        count[0] += 1
        if count[0] >= 3:
            t_holder[0].stop()
        timer_flush()

    t_holder.append(timer(cb))
    timer_flush()
    assert count[0] == 3


def test_timer_flush_observes_current_time() -> None:
    start = now()
    foos = [0]
    bars = [0]
    bazs = [0]
    foo = timer(lambda _e: (foos.__setitem__(0, foos[0] + 1), foo.stop()), 0, start + 1)
    bar = timer(lambda _e: (bars.__setitem__(0, bars[0] + 1), bar.stop()), 0, start)
    baz = timer(lambda _e: (bazs.__setitem__(0, bazs[0] + 1), baz.stop()), 0, start - 1)
    timer_flush()
    assert foos[0] == 0
    assert bars[0] == 1
    assert bazs[0] == 1
    foo.stop()
    bar.stop()
    baz.stop()
