# Direct Dependency License Review

This document records the direct dependency license review performed before the first public release.

| Dependency | Purpose | License |
|---|---|---|
| Flask | Runtime web framework | BSD-3-Clause |
| Gunicorn | Runtime WSGI server | MIT |
| pytest | Development / test runner | MIT |
| Ruff | Development / linting | MIT |
| Bandit | Development / static security analysis | Apache-2.0 |
| pip-audit | Development / dependency vulnerability audit | Apache-2.0 |

## Notes

- No copyleft direct dependency was identified in the current project configuration.
- The current direct dependency set is compatible with the project's MIT License.
- Development-only tools are not bundled as application source code.
- Dependency licenses must be rechecked when new direct dependencies are added or major packaging changes are introduced.
- The project license is MIT.
