# Public Release Checklist

The repository must remain private until all release-blocking items below are complete.

## Security
- [x] No API keys, tokens, passwords, or private keys detected in the tracked source.
- [x] No customer or personal data is stored in the repository.
- [x] No Eclipta Suite private source code is included.
- [x] Input values are validated by allow-list rules.
- [x] Assessment data contract/invariants are validated.
- [x] Mandatory authorized-use confirmation is enforced by the backend.
- [x] Result responses use `Cache-Control: no-store`.
- [x] Core browser security headers are set.
- [x] Ruff, Pytest, Bandit, and pip-audit run in CI.
- [x] Docker image build and runtime smoke tests pass in CI.

## Privacy / retention
- [x] No persistent assessment history.
- [x] No server-side HTML/PDF report archive.
- [x] No Flask session or assessment session cookie.
- [x] Operational logs do not contain assessment answers.

## Documentation
- [x] README contains local and Docker installation instructions.
- [x] README documents stateless behavior and usage authorization.
- [x] Architecture, scoring, retention and authorization rules are documented.
- [x] SECURITY.md is present.
- [x] CONTRIBUTING.md is present.
- [x] Direct dependency licenses are documented.
- [x] Distribution guide is present.
- [x] v0.1.0 release notes reflect current product behavior.

## Licensing
- [x] Project license selected: MIT.
- [x] LICENSE file added.
- [x] Direct dependency license review is compatible with MIT distribution.

## Packaging
- [x] Python source/wheel distributions build successfully in CI.
- [x] Wheel contains assessment JSON, HTML templates, CSS and JavaScript assets.
- [x] Clean-environment wheel smoke test passes in CI.
- [x] Docker image build and running-container smoke tests pass in CI.

## Release
- [x] Final CI is green on `main`.
- [ ] Repository visibility changed from private to public.
- [ ] First public release/tag created.
