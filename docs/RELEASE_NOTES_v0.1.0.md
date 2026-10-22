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
- stateless assessment flow with no persistent history
- mandatory authorized-use confirmation before submission
- no database, user account, AI provider, or external API requirement
- Docker / Docker Compose deployment
- direct Python installation
- MIT License

## Privacy and data handling

- assessment responses are not stored persistently
- no assessment history is created
- no server-side HTML/PDF report archive is maintained
- Flask session is not used for assessment results
- no session cookie is created for the assessment flow
- result responses use `Cache-Control: no-store`
- operational request logs do not contain assessment answers

## Security and quality

- backend-enforced authorized-use confirmation
- input allow-list validation
- assessment dataset/invariant validation
- CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy and Permissions-Policy
- Gunicorn production WSGI runtime
- Ruff
- Pytest
- Bandit
- pip-audit
- Docker build and runtime smoke verification
- Python wheel/runtime asset verification
- clean-environment wheel installation smoke test

## Distribution

Supported paths:

1. Docker / Docker Compose
2. Direct Python installation
3. GitHub release source archive

The Python package build is verified to contain the assessment JSON, HTML templates, CSS and JavaScript runtime assets.
