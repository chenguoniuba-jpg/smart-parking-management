# Smart Parking Management System

[Chinese version](README_ZH.md) · [English case study](project-intro/README.md) · [Maintainer role](MAINTAINER_ROLE.md) · [Deployment statement](DEPLOYMENT.md) · [Reuse guide](REUSE.md)

> **Start with the visual project story:** [Read the English case study →](project-intro/README.md)
>
> The repository also contains a standalone HTML presentation prepared for GitHub Pages. Its live URL can be added here after the public repository is created and Pages is enabled.

A FastAPI, SQLAlchemy, SQLite, and vanilla JavaScript parking-management system. Operational use began in March 2026 at a corporate industrial park parking facility in Shanghai. The running system was then iterated through later 2026 releases; this repository is the current August public-reuse snapshot.

## Repository history and release provenance

Development of the operating system predates this Git repository. Git was introduced when the completed project was prepared for public release, so the repository history begins with the `v1.0.0` public-release snapshot rather than the original development process. The dated January-August design files and changelog are retrospective historical design and iteration records; they do not represent corresponding Git commits. Changes made after publication are recorded with normal, current-date commits and releases.

> **Operational status and public-package boundary**
>
> - Operational use began in March 2026. Three administrators use the system to manage 286 parking spaces, and all application modules in this public edition are used on site.
> - Development continued after the March launch. As of this public snapshot, the maintainer states that the current public application source and the current on-site application source match. This does **not** mean the August snapshot existed unchanged in March.
> - The company name, exact address, credentials, personal information, live database, network settings, and raw operational records are not published.
> - The corporate industrial park management office can confirm the stated deployment. See the exact scope in [DEPLOYMENT.md](DEPLOYMENT.md).
> - Traffic estimates are deterministic historical baselines, not a trained machine-learning model.

![Dashboard marked as public sample data](images/dashboard.png)

The dashboard screenshot is **public sample data**. Its interface and 286-space capacity illustrate the reusable package; other displayed counts and percentages are not presented as live Shanghai operational statistics.

## What the repository contains

- JWT-protected administrator APIs and bcrypt password hashing.
- User, administrator, parking-space, parking-record, reservation, credit, point, configuration, and traffic-baseline models.
- Explainable space assignment using size, accessibility, and floor rules.
- Historical hourly baselines, long-stay alerts, and configurable capacity prompts.
- A browser management interface and automatic FastAPI API documentation.
- Automated API tests, a dependency lockfile, an environment template, container packaging, a SQLite backup utility, and GitHub Actions workflows.
- A GitHub-rendered [English case study](project-intro/README.md) and a standalone Pages presentation in [`project-intro/`](project-intro/).

## Architecture

```text
Browser SPA
    │  JWT-authenticated JSON requests
    ▼
FastAPI routers
    ├── authentication
    ├── users and parking spaces
    ├── records and reservations
    └── deterministic scheduling rules
    ▼
SQLAlchemy + SQLite
```

Camera, barrier-gate, payment, license-plate recognition, and live site connectors are not included. Reusers must integrate and validate those components for their own environment.

## Quick start

Requirements: Python 3.9+ and [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env
uv sync --frozen --extra dev
uv run --env-file .env python -m backend.init_data
uv run --env-file .env python -m backend.main
```

If `ADMIN_PASSWORD` is not set, the initializer prints a one-time generated password. For a controlled setup, set a strong value in your local `.env` or shell environment. Never commit `.env`.

- Application: <http://127.0.0.1:8000>
- API documentation: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

Production mode requires an explicit secret of at least 32 characters and exact allowed origins:

```bash
APP_ENV=production \
SECRET_KEY='replace-with-at-least-32-random-characters' \
CORS_ORIGINS='https://parking.example.com' \
uv run python -m backend.main
```

## Container start

```bash
cp .env.example .env
# Edit SECRET_KEY and ADMIN_PASSWORD before continuing.
docker compose run --rm app uv run python -m backend.init_data
docker compose up --build
```

The named Docker volume preserves the SQLite database. Container packaging does not add camera, gate, payment, proxy, TLS, monitoring, or production database infrastructure; those remain deployment-specific.

## Tests and package checks

```bash
uv run pytest
uv run ruff check --select F821,F822,F823 backend tests scripts
uv run python scripts/check_public_package.py
```

The package check rejects common secret files, local databases, OS metadata, and Office temporary files. GitHub Actions runs the automated test and public-package checks on pushes and pull requests.

## Back up the SQLite database

```bash
uv run python scripts/backup_sqlite.py --output-dir backups
```

The script uses SQLite's backup API and validates the resulting file. Copy backups to separately protected storage and test restoration according to your own retention policy.

## GitHub Pages

Visitors can enter the project story directly from this README through the [English case study](project-intro/README.md). The standalone HTML presentation is [`project-intro/project-intro.html`](project-intro/project-intro.html). The included Pages workflow publishes the `project-intro/` directory after Pages is configured to use **GitHub Actions** in the repository settings. The deployment URL will appear in the workflow's `github-pages` environment and should then replace this setup note with a direct live link.

## Interpreting the “smart” features

| Feature | Current implementation | What is not claimed |
|---|---|---|
| Traffic estimate | Counts historical entries by hour and reports a deterministic baseline | No trained model or validated forecast accuracy |
| Space assignment | Transparent score based on size, accessibility needs, and floor | No optimization proof or site-specific travel-time calibration in the public package |
| Capacity prompt | Alerts when occupancy exceeds a configured threshold | No automated physical expansion |
| Long-stay alert | Compares stored monthly days with a threshold | No legal or policy-enforcement decision |

## Maintainer role in the current public release

The current repository can document the maintainer's public-release stewardship without pretending that a clean snapshot proves sole authorship of every earlier line of code. For this release, the maintainer supplied and confirmed the operational scope, defined the public/private data boundary, preserved the July-to-August iteration chain, required corrections when claims exceeded the implementation, and reviewed the release for public reuse.

[Read the detailed role and attribution statement →](MAINTAINER_ROLE.md)

## Evidence, ownership, and AI assistance

- Repository maintainer: [chenguoniuba-jpg](https://github.com/chenguoniuba-jpg)
- [MAINTAINER_ROLE.md](MAINTAINER_ROLE.md) states what the current public package can support about the maintainer's role and what still requires personal confirmation.
- [DEPLOYMENT.md](DEPLOYMENT.md) separates confirmed deployment facts from private site data.
- [EVIDENCE_AND_LIMITATIONS.md](EVIDENCE_AND_LIMITATIONS.md) explains what can and cannot be verified from the repository.
- Seven Word files in `doc/product_mgt/` are design artifacts. The August v7 document records an iteration built on the July v6 baseline; file names and metadata alone are not independent proof of authorship, exact dates, site details, or measured outcomes.
- AI tools assisted with parts of documentation review, image labeling, and code refactoring. The maintainer remains responsible for verifying code, claims, and attribution before publication or application use.

## Documentation

- [Reuse and operations guide](REUSE.md)
- [Documentation index](doc/manual/INDEX.md)
- [Quick-start details](doc/manual/QUICKSTART.md)
- [Project structure](doc/manual/PROJECT_STRUCTURE.md)
- [Security policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)
- [Public release note](PUBLIC_RELEASE.md)
- [Maintainer role and attribution](MAINTAINER_ROLE.md)

Historical documents under `doc/manual/` preserve earlier requirements and design history. When they conflict with the current public claims, this README and `EVIDENCE_AND_LIMITATIONS.md` define the current public scope.

## Version and license

Public release version: **1.0.0**

Licensed under the [MIT License](LICENSE). Public visibility allows downloading; the license provides the actual reuse permission and conditions.
