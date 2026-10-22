# Distribution Guide

SiberKOBİ is designed to remain easy to obtain and run without proprietary infrastructure.

## Supported distribution methods

### 1. Docker / Docker Compose — recommended

This is the preferred method for most users because it isolates Python dependencies and gives the most reproducible installation.

```bash
git clone https://github.com/YagmurEr/siberkobi.git
cd siberkobi
docker compose up --build
```

Open:

```text
http://localhost:8000
```

### 2. Direct Python installation

Python 3.13 or newer:

```bash
git clone https://github.com/YagmurEr/siberkobi.git
cd siberkobi
python -m venv .venv
source .venv/bin/activate
pip install .
flask --app app:create_app run
```

Windows PowerShell:

```powershell
git clone https://github.com/YagmurEr/siberkobi.git
cd siberkobi
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install .
flask --app app:create_app run
```

### 3. GitHub release archive

Users may also download the source archive attached to a tagged GitHub release and follow the same Docker or Python installation steps.

## Packaging guarantees

CI verifies that:

- Python source distributions can be built.
- The wheel contains the assessment JSON data.
- HTML templates are included in the wheel.
- CSS and JavaScript runtime assets are included in the wheel.
- The Docker image builds successfully.
- Runtime dependencies pass vulnerability auditing.

## What is not required

The initial release does not require:

- PostgreSQL
- Redis
- a cloud account
- an API key
- an AI provider
- a user account

## Release policy

A tagged release must not be published unless CI is green on `main`.

The MIT license permits redistribution, modification, commercial use, and sublicensing, provided the copyright and license notice remain included.
