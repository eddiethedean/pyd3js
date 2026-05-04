# Roadmap

`pyd3js-path` targets upstream `d3-path` parity for the pinned version in `upstream_lock.json`.

Current status (0.1.0):

- Full export parity for `d3-path@3.1.0`
- Ported upstream JS tests (Python)
- Vendored upstream JS test-suite gate (Mocha) via `pytest -m upstream`
- Oracle parity checks via `pytest -m oracle`

