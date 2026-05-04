from __future__ import annotations

from typing import Any

from pyd3js_selection.namespaces import namespaces


def namespace(name: Any):
    """Return either a local name string, or {space, local} for known namespaces."""
    name = str(name)
    i = name.find(":")
    if i >= 0 and name[:i] != "xmlns":
        prefix = name[:i]
        local = name[i + 1 :]
        uri = namespaces.get(prefix)
        if uri:
            return {"space": uri, "local": local}
        return local

    if i >= 0 and name[:i] == "xmlns":
        uri = namespaces.get("xmlns")
        if uri:
            return {"space": uri, "local": name}
        return name

    uri = namespaces.get(name)
    if uri:
        return {"space": uri, "local": name}
    return name
