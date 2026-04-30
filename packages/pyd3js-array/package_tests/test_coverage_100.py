from __future__ import annotations

from typing import Any, cast


import pytest

from pyd3js_array.bin import bin
from pyd3js_array.blur import blur, blur2, blurImage
from pyd3js_array.count import count
from pyd3js_array.cumsum import cumsum
from pyd3js_array.every import every
from pyd3js_array.filter import filter
from pyd3js_array.fsum import Adder, fcumsum, fsum
from pyd3js_array.intern import InternMap, InternSet
from pyd3js_array.map import map
from pyd3js_array.max_index import maxIndex
from pyd3js_array.min_index import minIndex
from pyd3js_array.mode import mode
from pyd3js_array.quantile_index import quantileIndex
from pyd3js_array.reduce import reduce
from pyd3js_array.some import some
from pyd3js_array.threshold_sturges import thresholdSturges


def test_every_filter_some_type_errors() -> None:
    with pytest.raises(TypeError, match="test is not a function"):
        every([1, 2, 3], cast(Any, None))
    with pytest.raises(TypeError, match="test is not a function"):
        some([1, 2, 3], cast(Any, None))
    with pytest.raises(TypeError, match="test is not a function"):
        filter([1, 2, 3], cast(Any, None))


def test_map_type_error_on_mapper() -> None:
    with pytest.raises(TypeError, match="mapper is not a function"):
        map([1, 2, 3], cast(Any, None))


def test_reduce_type_error_on_reducer() -> None:
    with pytest.raises(TypeError, match="reducer is not a function"):
        reduce([1, 2], cast(Any, None))


def test_count_and_cumsum_accessor_branches() -> None:
    data = [{"v": "2"}, {"v": None}, {"v": "nope"}, {"v": 3}]
    assert count(data, lambda d, i, values: d["v"]) == 2
    assert cumsum(data, lambda d, i, values: d["v"]) == [2.0, 2.0, 2.0, 5.0]


def test_fsum_and_fcumsum_accessor_branches() -> None:
    data = [{"v": 0}, {"v": "2"}, {"v": None}, {"v": 3}]
    assert fsum(data, lambda d, i, values: d["v"]) == 5.0
    assert fcumsum(data, lambda d, i, values: d["v"]) == [0.0, 2.0, 2.0, 5.0]


def test_adder_rounding_correction_branch_executes() -> None:
    # Exercise Adder.valueOf's post-loop correction branch by constructing
    # partials with same sign around a non-zero lo.
    a = Adder()
    a.add(1e16).add(1.0).add(-1e16).add(1.0)
    assert float(a) == 2.0


def test_internmap_internset_edge_cases() -> None:
    m: InternMap[str, int] = InternMap()
    m["a"] = 1
    del m["a"]  # __delitem__
    assert m.delete("missing") is False

    m2 = InternMap([("a", 1), ("b", 2)])
    assert list(m2.keys()) == ["a", "b"]
    assert list(m2.values()) == [1, 2]
    assert m2.get("missing", 9) == 9

    class Boom:
        def __call__(self, _x):  # pragma: no cover
            raise RuntimeError("boom")

    s: InternSet[object] = InternSet(key=Boom())  # type: ignore[arg-type]
    assert ("x" in s) is False  # __contains__ exception path

    s2: InternSet[str] = InternSet(["a"])
    assert s2.delete("missing") is False
    assert s2.delete("a") is True


def test_min_max_index_accessor_branches() -> None:
    data = [{"v": 5}, {"v": 2}, {"v": None}, {"v": 9}]
    assert minIndex(data, lambda d, i, values: d["v"]) == 1
    assert maxIndex(data, lambda d, i, values: d["v"]) == 3


def test_mode_accessor_branch() -> None:
    data = [{"v": "a"}, {"v": None}, {"v": float("nan")}, {"v": "b"}, {"v": "a"}]
    assert mode(data, lambda d, i, values: d["v"]) == "a"


def test_quantile_index_valueof_and_all_invalid() -> None:
    data = [{"v": None}, {"v": "nope"}]
    assert quantileIndex(data, 0.5, lambda d, i, values: d["v"]) == -1
    assert quantileIndex(data, 0, lambda d, i, values: d["v"]) == -1
    assert quantileIndex(data, 1, lambda d, i, values: d["v"]) == -1


def test_bin_thresholds_callable_returning_int() -> None:
    b = bin().domain([0, 10]).thresholds(lambda nums, x0, x1: thresholdSturges(nums))
    out = b([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    assert len(out) >= 1


def test_blur_guard_and_error_paths() -> None:
    with pytest.raises(ValueError, match="invalid r"):
        blur([1.0, 2.0], -1)
    with pytest.raises(ValueError, match="invalid rx"):
        blur2(cast(Any, {"data": [1.0], "width": 1, "height": 1}), -1)
    with pytest.raises(ValueError, match="invalid ry"):
        blur2(cast(Any, {"data": [1.0], "width": 1, "height": 1}), 1, -1)
    with pytest.raises(ValueError, match="invalid width"):
        blur2(cast(Any, {"data": [1.0], "width": -1, "height": 1}), 1)
    with pytest.raises(ValueError, match="invalid height"):
        blur2(cast(Any, {"data": [1.0], "width": 1, "height": -1}), 1)

    # width==0 early return
    data = {"data": [1.0, 2.0, 3.0], "width": 0}
    assert blur2(cast(Any, data), 1) is data


def test_blur2_height_default_and_blury_only_branch() -> None:
    # height omitted -> computed; rx=0 -> blury-only branch
    data = {"data": [0.0, 10.0, 0.0, 0.0], "width": 2}
    out = blur2(cast(Any, data), 0, 1)
    assert out is data
    assert any(x != 0.0 for x in out["data"])


def test_blurimage_executes_channel_blur_path() -> None:
    img = {"data": [255.0, 0.0, 0.0, 255.0] * 2, "width": 2, "height": 1}
    out = blurImage(cast(Any, img), 1)
    assert out is img
    assert len(out["data"]) == 8


def test_blur_internal_stop_before_start_guards() -> None:
    import importlib

    blur_mod = importlib.import_module("pyd3js_array.blur")

    T = [0.0]
    S = [1.0]
    blur_mod._bluri(1)(T, S, 0, 0, 1)
    blur_mod._blurf(1.5)(T, S, 0, 0, 1)


def test_blur_fractional_radius_and_blurx_only_branch() -> None:
    a = [0.0, 10.0, 0.0]
    blur(a, 1.5)

    data = {"data": [0.0, 10.0, 0.0, 0.0], "width": 2}
    out = blur2(cast(Any, data), 1, 0)  # blurx-only branch
    assert out is data


def test_threshold_guard_branches() -> None:
    from pyd3js_array.threshold_freedman_diaconis import thresholdFreedmanDiaconis
    from pyd3js_array.threshold_scott import thresholdScott
    from pyd3js_array.threshold_sturges import thresholdSturges

    assert thresholdSturges([]) == 1
    assert thresholdScott([], 0, 1) == 1

    # Deviation returns None for <2 observed values
    assert thresholdScott([1.0], 0, 1) == 1
    # k <= 0 -> guard
    assert thresholdScott([1.0, 2.0, 3.0, 4.0], 10, 0) == 1

    # iqr == 0 -> guard
    assert thresholdFreedmanDiaconis([1, 1, 1, 1], 1, 1) == 1
    # n <= 0 (all invalid) -> guard
    assert thresholdFreedmanDiaconis([float("nan")], 0, 1) == 1
    # k <= 0 -> guard
    assert thresholdFreedmanDiaconis([1.0, 2.0, 3.0, 4.0], 10, 0) == 1


def test_internmap_iter_covers_iterator() -> None:
    m = InternMap([("a", 1), ("b", 2)])
    assert list(iter(m)) == ["a", "b"]


def test_adder_valueof_correction_branch_direct_state() -> None:
    # Force the valueOf correction branch deterministically.
    a = Adder()
    a._partials[0] = 1.0
    a._partials[1] = 2**-53
    a._partials[2] = 1.0
    a._n = 3
    assert a.valueOf() == 1.0 + 2**-52


def test_fcumsum_nan_path() -> None:
    out = fcumsum([float("nan"), 1.0])
    assert out == [0.0, 1.0]
