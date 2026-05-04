import math
import re

import pytest

from pyd3js_path import path


_RE_NUMBER = re.compile(r"[-+]?(?:\d+\.\d+|\d+\.|\.\d+|\d+)(?:[eE][-]?\d+)?")


def _format_number(m: re.Match[str]) -> str:
    s = float(m.group(0))
    if abs(s - round(s)) < 1e-6:
        return str(int(round(s)))
    return f"{s:.6f}"


def normalize_path(p: str) -> str:
    return _RE_NUMBER.sub(_format_number, p)


def assert_path_equal(actual, expected: str) -> None:
    assert normalize_path(str(actual)) == normalize_path(str(expected))


def test_path_is_instanceof_path() -> None:
    p = path()
    assert isinstance(p, path)
    assert_path_equal(p, "")


def test_move_to_appends_m() -> None:
    p = path()
    p.moveTo(150, 50)
    assert_path_equal(p, "M150,50")
    p.lineTo(200, 100)
    assert_path_equal(p, "M150,50L200,100")
    p.moveTo(100, 50)
    assert_path_equal(p, "M150,50L200,100M100,50")


def test_close_path_appends_z() -> None:
    p = path()
    p.moveTo(150, 50)
    assert_path_equal(p, "M150,50")
    p.closePath()
    assert_path_equal(p, "M150,50Z")
    p.closePath()
    assert_path_equal(p, "M150,50ZZ")


def test_close_path_empty_does_nothing() -> None:
    p = path()
    assert_path_equal(p, "")
    p.closePath()
    assert_path_equal(p, "")


def test_line_to_appends_l() -> None:
    p = path()
    p.moveTo(150, 50)
    assert_path_equal(p, "M150,50")
    p.lineTo(200, 100)
    assert_path_equal(p, "M150,50L200,100")
    p.lineTo(100, 50)
    assert_path_equal(p, "M150,50L200,100L100,50")


def test_quadratic_curve_to_appends_q() -> None:
    p = path()
    p.moveTo(150, 50)
    assert_path_equal(p, "M150,50")
    p.quadraticCurveTo(100, 50, 200, 100)
    assert_path_equal(p, "M150,50Q100,50,200,100")


def test_bezier_curve_to_appends_c() -> None:
    p = path()
    p.moveTo(150, 50)
    assert_path_equal(p, "M150,50")
    p.bezierCurveTo(100, 50, 0, 24, 200, 100)
    assert_path_equal(p, "M150,50C100,50,0,24,200,100")


def test_arc_throws_if_radius_negative() -> None:
    p = path()
    p.moveTo(150, 100)
    with pytest.raises(ValueError, match="negative radius"):
        p.arc(100, 100, -50, 0, math.pi / 2)


def test_arc_m_only_if_radius_zero_empty_path() -> None:
    p = path()
    p.arc(100, 100, 0, 0, math.pi / 2)
    assert_path_equal(p, "M100,100")


def test_arc_l_only_if_radius_zero_nonempty_path() -> None:
    p = path()
    p.moveTo(0, 0)
    p.arc(100, 100, 0, 0, math.pi / 2)
    assert_path_equal(p, "M0,0L100,100")


def test_arc_m_only_if_angle_zero() -> None:
    p = path()
    p.arc(100, 100, 0, 0, 0)
    assert_path_equal(p, "M100,100")


def test_arc_m_only_if_angle_near_zero() -> None:
    p = path()
    p.arc(100, 100, 0, 0, 1e-16)
    assert_path_equal(p, "M100,100")


def test_arc_m_if_path_was_empty() -> None:
    p1 = path()
    p1.arc(100, 100, 50, 0, math.pi * 2)
    assert_path_equal(p1, "M150,100A50,50,0,1,1,50,100A50,50,0,1,1,150,100")
    p2 = path()
    p2.arc(0, 50, 50, -math.pi / 2, 0)
    assert_path_equal(p2, "M0,0A50,50,0,0,1,50,50")


def test_arc_appends_l_if_not_start_at_current_point() -> None:
    p = path()
    p.moveTo(100, 100)
    p.arc(100, 100, 50, 0, math.pi * 2)
    assert_path_equal(p, "M100,100L150,100A50,50,0,1,1,50,100A50,50,0,1,1,150,100")


def test_arc_appends_single_a_less_than_pi() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, math.pi / 2)
    assert_path_equal(p, "M150,100A50,50,0,0,1,100,150")


def test_arc_appends_single_a_less_than_tau() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, math.pi * 1)
    assert_path_equal(p, "M150,100A50,50,0,1,1,50,100")


def test_arc_appends_two_a_if_greater_than_tau() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, math.pi * 2)
    assert_path_equal(p, "M150,100A50,50,0,1,1,50,100A50,50,0,1,1,150,100")


def test_arc_small_cw_false() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, math.pi / 2, False)
    assert_path_equal(p, "M150,100A50,50,0,0,1,100,150")


def test_arc_small_cw() -> None:
    p = path()
    p.moveTo(100, 50)
    p.arc(100, 100, 50, -math.pi / 2, 0, False)
    assert_path_equal(p, "M100,50A50,50,0,0,1,150,100")


def test_arc_ccw_circle_near_zero() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, 1e-16, True)
    assert_path_equal(p, "M150,100A50,50,0,1,0,50,100A50,50,0,1,0,150,100")


def test_arc_cw_draws_nothing_near_zero() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, 1e-16, False)
    assert_path_equal(p, "M150,100")


def test_arc_ccw_draws_nothing_negative_near_zero() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, -1e-16, True)
    assert_path_equal(p, "M150,100")


def test_arc_cw_circle_negative_near_zero() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, -1e-16, False)
    assert_path_equal(p, "M150,100A50,50,0,1,1,50,100A50,50,0,1,1,150,100")


def test_arc_ccw_tau_circle() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, 2 * math.pi, True)
    assert_path_equal(p, "M150,100A50,50,0,1,0,50,100A50,50,0,1,0,150,100")


def test_arc_cw_tau_circle() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, 2 * math.pi, False)
    assert_path_equal(p, "M150,100A50,50,0,1,1,50,100A50,50,0,1,1,150,100")


def test_arc_ccw_tau_plus_epsilon_circle() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, 2 * math.pi + 1e-13, True)
    assert_path_equal(p, "M150,100A50,50,0,1,0,50,100A50,50,0,1,0,150,100")


def test_arc_cw_tau_minus_epsilon_circle() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, 2 * math.pi - 1e-13, False)
    assert_path_equal(p, "M150,100A50,50,0,1,1,50,100A50,50,0,1,1,150,100")


def test_arc_0_to_13pi_over_2_cw_circle() -> None:
    p = path()
    p.moveTo(150, 100)
    p.arc(100, 100, 50, 0, 13 * math.pi / 2, False)
    assert_path_equal(p, "M150,100A50,50,0,1,1,50,100A50,50,0,1,1,150,100")


def test_arc_13pi_over_2_to_0_big_cw_arc() -> None:
    p = path()
    p.moveTo(100, 150)
    p.arc(100, 100, 50, 13 * math.pi / 2, 0, False)
    assert_path_equal(p, "M100,150A50,50,0,1,1,150,100")


def test_arc_pi_over_2_to_0_big_cw_arc() -> None:
    p = path()
    p.moveTo(100, 150)
    p.arc(100, 100, 50, math.pi / 2, 0, False)
    assert_path_equal(p, "M100,150A50,50,0,1,1,150,100")


def test_arc_3pi_over_2_to_0_small_cw_arc() -> None:
    p = path()
    p.moveTo(100, 50)
    p.arc(100, 100, 50, 3 * math.pi / 2, 0, False)
    assert_path_equal(p, "M100,50A50,50,0,0,1,150,100")


def test_arc_truthy_ccw() -> None:
    for trueish in [1, "1", True, 10, "3", "string"]:
        p = path()
        p.moveTo(100, 150)
        p.arc(100, 100, 50, math.pi / 2, 0, trueish)
        assert_path_equal(p, "M100,150A50,50,0,0,0,150,100")


def test_arc_falsy_cw() -> None:
    for falseish in [0, None]:
        p = path()
        p.moveTo(150, 100)
        p.arc(100, 100, 50, 0, math.pi / 2, falseish)
        assert_path_equal(p, "M150,100A50,50,0,0,1,100,150")


def test_arc_to_negative_raises() -> None:
    p = path()
    p.moveTo(150, 100)
    with pytest.raises(ValueError, match="negative radius"):
        p.arcTo(270, 39, 163, 100, -53)


def test_arc_to_appends_m_if_empty() -> None:
    p = path()
    p.arcTo(270, 39, 163, 100, 53)
    assert_path_equal(p, "M270,39")


def test_arc_to_does_nothing_if_prev_point_is_x1y1() -> None:
    p = path()
    p.moveTo(270, 39)
    p.arcTo(270, 39, 163, 100, 53)
    assert_path_equal(p, "M270,39")


def test_arc_to_collinear_appends_l() -> None:
    p = path()
    p.moveTo(100, 50)
    p.arcTo(101, 51, 102, 52, 10)
    assert_path_equal(p, "M100,50L101,51")


def test_arc_to_coincident_x1_x2_appends_l() -> None:
    p = path()
    p.moveTo(100, 50)
    p.arcTo(101, 51, 101, 51, 10)
    assert_path_equal(p, "M100,50L101,51")


def test_arc_to_radius_zero_appends_l() -> None:
    p = path()
    p.moveTo(270, 182)
    p.arcTo(270, 39, 163, 100, 0)
    assert_path_equal(p, "M270,182L270,39")


def test_arc_to_appends_l_and_a_when_not_start_at_current_point() -> None:
    p1 = path()
    p1.moveTo(270, 182)
    p1.arcTo(270, 39, 163, 100, 53)
    assert_path_equal(p1, "M270,182L270,130.222686A53,53,0,0,0,190.750991,84.179342")

    p2 = path()
    p2.moveTo(270, 182)
    p2.arcTo(270, 39, 363, 100, 53)
    assert_path_equal(p2, "M270,182L270,137.147168A53,53,0,0,1,352.068382,92.829799")


def test_arc_to_appends_only_a_if_starts_at_current_point() -> None:
    p = path()
    p.moveTo(100, 100)
    p.arcTo(200, 100, 200, 200, 100)
    assert_path_equal(p, "M100,100A100,100,0,0,1,200,200")


def test_arc_to_sets_last_point_to_end_tangent() -> None:
    p = path()
    p.moveTo(100, 100)
    p.arcTo(200, 100, 200, 200, 50)
    p.arc(150, 150, 50, 0, math.pi)
    assert_path_equal(p, "M100,100L150,100A50,50,0,0,1,200,150A50,50,0,1,1,100,150")


def test_rect_appends_m_h_v_h_z() -> None:
    p = path()
    p.moveTo(150, 100)
    p.rect(100, 200, 50, 25)
    assert_path_equal(p, "M150,100M100,200h50v25h-50Z")
