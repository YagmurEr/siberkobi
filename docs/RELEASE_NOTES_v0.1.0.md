# SiberKOBİ v0.1.0

First public release candidate.

## Highlights

- 25-question cybersecurity self-assessment for SMEs
- 5 security domains
- deterministic scoring and category results
- conditional "Uygulanamaz" support
- responsive HTML interface
- HTML result and improvement report
- browser print / PDF save support
- no database, user account, AI provider, or external API requirement
- Docker / Docker Compose deployment
- direct Python installation
- MIT License

## Security and quality

- input allow-list validation
- no persistent assessment data
- `Cache-Control: no-store` on result responses
- CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy and Permissions-Policy
- Ruff
- Pytest
- Bandit
- pip-audit
- Docker build verification
- Python wheel/runtime asset verification

## Distribution

Supported paths:

1. Docker / Docker Compose
2. Direct Python installation
3. GitHub release source archive

The Python package build is verified to contain the assessment JSON, HTML templates, CSS and JavaScript runtime assets.
