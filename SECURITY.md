## Security policy

### Reporting a vulnerability

Please **do not** open a public GitHub issue for security-sensitive reports.

Instead, use **GitHub Security Advisories**:

- Go to the repo’s **Security** tab → **Advisories** → **New draft security advisory**
- Include:
  - A clear description of the issue and impact
  - Reproduction steps (minimal PoC if possible)
  - Affected package(s) under `packages/` and versions/commits tested
  - Any suggested fix or mitigation (if you have one)

If you cannot use GitHub advisories, open a minimal issue that says you have a
security report and request a private contact channel (do not include details).

### Supported versions

This repository is a monorepo of independently versioned distributions under
`packages/`. We aim to fix security issues in:

- The **latest released version** of each `pyd3js-*` package
- The current `main` branch

Where feasible, we’ll backport critical fixes to recently released versions, but
we may ask you to upgrade to the latest patch/minor release.

### What to expect

- **Acknowledgement**: typically within a few business days
- **Fix timeline**: depends on severity and complexity; we’ll coordinate in the
  advisory thread
- **Disclosure**: we prefer coordinated disclosure once a fix is available

### Security checks in CI

We run automated security checks in GitHub Actions, including CodeQL and
dependency auditing for the Python workspace and the Node-based oracle tooling.

