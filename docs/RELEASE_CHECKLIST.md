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
- [x] Distribution guide is present.

## Licensing
- [x] Project license selected: MIT.
- [x] LICENSE file added.
- [x] Direct dependency license review is compatible with MIT distribution.

## Packaging
- [x] Python source/wheel distributions build successfully in CI.
- [x] Wheel contains assessment JSON, HTML templates, CSS and JavaScript assets.
- [x] Docker image build passes in CI.

## Release
- [x] Final CI is green on `main`.
- [ ] Repository visibility changed from private to public.
- [ ] First public release/tag created.
