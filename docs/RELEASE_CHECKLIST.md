# Public Release Checklist

The repository must remain private until all release-blocking items below are complete.

## Security
- [x] No API keys, tokens, passwords, or private keys detected in the tracked source.
- [x] No customer or personal data is stored in the repository.
- [x] No Eclipta Suite private source code is included.
- [x] Input values are validated by allow-list rules.
- [x] Result responses use `Cache-Control: no-store`.
- [x] Core browser security headers are set.
- [x] Ruff, Pytest, Bandit, and pip-audit run in CI.
- [x] Docker image build passes in CI.

## Documentation
- [x] README contains local and Docker installation instructions.
- [x] Architecture and scoring logic are documented.
- [x] SECURITY.md is present.
- [x] CONTRIBUTING.md is present.
- [x] Direct dependency licenses are documented.

## Licensing
- [ ] Project license selected.
- [ ] LICENSE file added.
- [ ] Dependency license review confirmed against selected project license.

## Release
- [ ] Final CI is green on `main`.
- [ ] Repository visibility changed from private to public.
- [ ] First public release/tag created.
