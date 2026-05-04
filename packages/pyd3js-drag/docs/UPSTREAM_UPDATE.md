# Upstream update checklist (d3-drag)

Pinned version is tracked in `upstream_lock.json`.

When bumping `d3-drag`, update:

- `packages/pyd3js-drag/upstream/d3-drag` via `python scripts/vendor_upstream.py`
- `docs/UPSTREAM_API.md` export inventory
- `README.md` compatibility matrix
- Port / adjust `package_tests/test_upstream_port_*` as needed
- Ensure upstream Mocha gate passes (`pytest -m upstream`), and Python tests + coverage remain green

