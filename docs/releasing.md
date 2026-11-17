# Releasing OpenContext

The repository has two publishable artifacts:

- Python distribution `opencontext-video`, including the `opencontext` CLI.
- npm package `@kylosonic/opencontext-schemas`.

Versions are currently `0.1.0` in both package manifests. A Git tag must be
`v0.1.0` (without extra text), and the release workflow verifies that the tag,
npm version, and Python version match before building.

## Protected publishing

`.github/workflows/release.yml` runs on `v*` tags. Publishing jobs use GitHub
Environments named `pypi` and `npm`. A pushed tag therefore builds and verifies
the release without publishing until an environment is approved manually.

- PyPI uses Trusted Publishing through GitHub OIDC; no PyPI token is stored.
- npm requires an `NPM_TOKEN` repository secret and publishes with provenance.

Before the first release:

1. In PyPI, add a pending Trusted Publisher for `opencontext-video` with
   owner `kylosonic`, repository `opencontext`, workflow `release.yml`, and
   environment `pypi`.
2. Create an npm granular access token that can publish
   `@kylosonic/opencontext-schemas` under the `@kylosonic` scope. Store it as
   the repository secret `NPM_TOKEN`.
3. In repository Settings → Environments, add required reviewers to `pypi` and
   `npm`. This is the human approval gate for publishing.

## Release checklist

1. Update `CHANGELOG.md` and both package versions.
2. Run the full local verification commands from `CONTRIBUTING.md`.
3. Commit and merge the release changes.
4. Create and push a matching tag, for example `git tag v0.1.0 && git push origin v0.1.0`.
5. Approve the `pypi` and `npm` environments after the verification job passes.
6. Confirm both package pages and install the published artifacts in a clean environment.
