# Upstream update checklist (d3-selection)

Pinned version is tracked in `upstream_lock.json`.

When bumping `d3-selection`, update:

- `packages/pyd3js-selection/upstream/d3-selection` via `python scripts/vendor_upstream.py`
- `docs/UPSTREAM_API.md` export inventory
- `README.md` compatibility matrix
- Port / adjust `package_tests/test_upstream_port_*` as needed
- Ensure upstream Mocha gate passes (`pytest -m upstream`), and Python tests + coverage remain green

