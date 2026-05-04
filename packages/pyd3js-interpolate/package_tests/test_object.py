from __future__ import annotations

from pyd3js_interpolate import interpolateObject


def test_interpolate_object() -> None:
    assert interpolateObject({"a": 2, "b": 12}, {"a": 4, "b": 24})(0.5) == {
        "a": 3,
        "b": 18,
    }

    class A:
        b = 12

        def __init__(self, a: float) -> None:
            self.a = a

    assert interpolateObject(A(2), {"a": 4, "b": 12})(0.5) == {"a": 3, "b": 12}
    assert interpolateObject({"a": 2, "b": 12}, A(4))(0.5) == {"a": 3, "b": 12}
    assert interpolateObject(A(4), A(2))(0.5) == {"a": 3, "b": 12}

    assert interpolateObject({"background": "red"}, {"background": "green"})(0.5) == {
        "background": "rgb(128, 64, 0)"
    }
    assert interpolateObject({"foo": [2, 12]}, {"foo": [4, 24]})(0.5) == {
        "foo": [3, 18]
    }
    assert interpolateObject({"foo": {"bar": [2, 12]}}, {"foo": {"bar": [4, 24]}})(
        0.5
    ) == {"foo": {"bar": [3, 18]}}
    assert interpolateObject({"foo": 2, "bar": 12}, {"foo": 4})(0.5) == {"foo": 3}
    assert interpolateObject({"foo": 2}, {"foo": 4, "bar": 12})(0.5) == {
        "foo": 3,
        "bar": 12,
    }

    assert interpolateObject(float("nan"), {"foo": 2})(0.5) == {"foo": 2}
    assert interpolateObject({"foo": 2}, None)(0.5) == {}
    assert interpolateObject(None, {"foo": 2})(0.5) == {"foo": 2}
    assert interpolateObject({"foo": 2}, None)(0.5) == {}
    assert interpolateObject(None, float("nan"))(0.5) == {}

    o = interpolateObject({"foo": 0}, {"foo": 2})
    assert o(0.5) == {"foo": 1}
