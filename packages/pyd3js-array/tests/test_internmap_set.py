from __future__ import annotations

import pytest

from pyd3js_array.intern import InternMap, InternSet


def test_internmap_basic_mapping_and_order() -> None:
    m: InternMap[str, int] = InternMap([("a", 1), ("b", 2)])
    assert list(m.items()) == [("a", 1), ("b", 2)]
    assert m.get("a") == 1
    assert m.has("b") is True
    assert m.delete("b") is True
    assert m.has("b") is False


def test_internmap_key_canonicalizer_collides_keys() -> None:
    m: InternMap[object, str] = InternMap(key=lambda o: "same")
    a = object()
    b = object()
    m.set(a, "first")
    m.set(b, "second")
    # Same canonical key means last write wins, but we preserve the last-seen original key.
    assert len(m) == 1
    assert list(m.items()) == [(b, "second")]
    assert m.get(a) == "second"


def test_internset_key_canonicalizer_collides_values() -> None:
    s: InternSet[object] = InternSet(key=lambda o: 1)
    a = object()
    b = object()
    s.add(a).add(b)
    assert len(s) == 1
    assert list(s) == [b]
    assert s.has(a) is True


@pytest.mark.oracle
def test_internmap_set_match_oracle_for_primitives(require_oracle: None) -> None:
    from tests.oracle.client import oracle_eval

    py = list(InternMap([("a", 1), ("b", 2)]).items())
    js = oracle_eval(
        "(function(){ return Array.from(new d3.InternMap([['a',1],['b',2]])); })()"
    )
    assert py == [tuple(x) for x in js]

    py_set = list(InternSet(["a", "b"]))
    js_set = oracle_eval(
        "(function(){ return Array.from(new d3.InternSet(['a','b'])); })()"
    )
    assert py_set == js_set
