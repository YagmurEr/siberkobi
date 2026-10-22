# Contributing to SiberKOBİ

Thank you for contributing.

## Development principles

- Keep the project simple, modular, and self-hostable.
- Do not copy code from Eclipta Suite or any private repository.
- Do not add telemetry, user tracking, external AI, or third-party API dependencies without an explicit project decision.
- Keep assessment questions and evaluation rules separate from presentation code.
- Do not weaken input validation or security response headers.
- Do not commit credentials, personal data, customer data, or private infrastructure details.

## Local checks

Before opening a pull request, run:

```bash
ruff check .
pytest -q
bandit -r app
pip-audit
docker build -t siberkobi:test .
```

## Pull requests

A pull request should:

- explain the problem and proposed change
- include tests for changed behavior
- keep documentation current
- pass CI
- avoid unrelated refactoring

Changes to assessment questions, scoring rules, branding, licensing, or data collection are product decisions and should be discussed before implementation.
