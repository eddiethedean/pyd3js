from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

_SENTINEL = object()


@dataclass
class _Listener:
    name: str
    value: Callable[..., Any]


def _illegal_type(t: str) -> bool:
    return not t or re.search(r"[\s.]", t) is not None


def dispatch(*typenames: str) -> Dispatch:
    table: Dict[str, List[_Listener]] = {}
    for raw in typenames:
        t = str(raw)
        if _illegal_type(t) or t in table:
            raise ValueError(f"illegal type: {raw}")
        table[t] = []
    return Dispatch(table)


def _parse_typenames(typenames: str, types: Dict[str, List[_Listener]]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for part in re.split(r"\s+", typenames.strip()):
        if not part:
            continue
        name = ""
        i = part.find(".")
        if i >= 0:
            name = part[i + 1 :]
            t = part[:i]
        else:
            t = part
        if t and t not in types:
            raise ValueError(f"unknown type: {t}")
        out.append((t, name))
    return out


def _get(lst: List[_Listener], name: str) -> Optional[Callable[..., Any]]:
    for c in lst:
        if c.name == name:
            return c.value
    return None


def _set(
    lst: List[_Listener], name: str, callback: Optional[Callable[..., Any]]
) -> List[_Listener]:
    new_list = [c for c in lst if c.name != name]
    if callback is not None:
        new_list.append(_Listener(name=name, value=callback))
    return new_list


class Dispatch:
    __slots__ = ("_",)

    def __init__(self, table: Dict[str, List[_Listener]]) -> None:
        self._ = table

    def on(
        self,
        typename: str,
        callback: Any = _SENTINEL,
    ) -> Union["Dispatch", Optional[Callable[..., Any]]]:
        T = _parse_typenames(str(typename), self._)
        if callback is _SENTINEL:
            for tname, nm in T:
                if tname and (cb := _get(self._[tname], nm)) is not None:
                    return cb
            return None
        if callback is not None and not callable(callback):
            raise ValueError(f"invalid callback: {callback}")
        for tname, nm in T:
            if tname:
                self._[tname] = _set(self._[tname], nm, callback)
            elif callback is None:
                for t in self._:
                    self._[t] = _set(self._[t], nm, None)
        return self

    def copy(self) -> Dispatch:
        return Dispatch({k: list(v) for k, v in self._.items()})

    def call(self, typ: str, that: Any, *args: Any) -> None:
        if typ not in self._:
            raise ValueError(f"unknown type: {typ}")
        for c in self._[typ]:
            c.value(that, *args)

    def apply(self, typ: str, that: Any, args: List[Any]) -> None:
        if typ not in self._:
            raise ValueError(f"unknown type: {typ}")
        for c in self._[typ]:
            c.value(that, *args)


__all__ = ["dispatch", "Dispatch"]
