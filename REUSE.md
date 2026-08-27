# Reuse and operations guide

This guide covers the reusable public package. It does not disclose or reproduce private Shanghai runtime configuration.

## 1. Choose a deployment profile

- **Local evaluation:** SQLite, localhost binding, generated or locally supplied administrator password.
- **Small controlled deployment:** container image, persistent volume, reverse proxy with TLS, restricted CORS, protected secrets, tested backups, centralized logs, and access monitoring.
- **Integrated facility deployment:** all of the above plus site-specific identity, camera, gate, plate-recognition, payment, network segmentation, privacy, and incident-response controls.

The repository supplies the first profile and a container baseline for the second. It does not claim to be a turnkey hardware or compliance package.

## 2. Configure without committing secrets

Copy `.env.example` to `.env`, then change at least `SECRET_KEY` and `ADMIN_PASSWORD`. Production startup rejects a missing or short `SECRET_KEY` and wildcard CORS origins.

Supported application variables:

| Variable | Purpose | Safe starting point |
|---|---|---|
| `APP_ENV` | Enables production validation | `production` outside local development |
| `SECRET_KEY` | Signs JWT tokens | Random secret of 32+ characters |
| `HOST` / `PORT` | Bind address and port for direct runs | `127.0.0.1` / `8000` locally |
| `CORS_ORIGINS` | Browser origins allowed to call the API | Exact HTTPS origin(s) |
| `DATABASE_URL` | SQLAlchemy connection URL | SQLite file for evaluation |
| `ADMIN_*` | Initial administrator created by the initializer | Site-owned credentials |

Rotate secrets according to local policy. Changing `SECRET_KEY` invalidates existing sessions.

## 3. Reproduce dependencies and verify the package

```bash
uv sync --frozen --extra dev
uv run pytest
uv run ruff check --select F821,F822,F823 backend tests scripts
uv run python scripts/check_public_package.py
```

`uv.lock` makes dependency resolution repeatable. Review and update dependencies deliberately; rerun the full checks after every lockfile change.

The repository includes China-accessible package indexes for the maintainer's environment. Reusers may override the index with uv's standard environment or command-line configuration while retaining lockfile hash verification.

## 4. Initialize and run

Local:

```bash
uv run --env-file .env python -m backend.init_data
uv run --env-file .env python -m backend.main
```

Docker:

```bash
docker compose run --rm app uv run python -m backend.init_data
docker compose up --build
```

The initializer is idempotent for its administrator, sample users, spaces, and configuration keys. Its records are public example data, not copied site records.

## 5. Health, logs, and monitoring

- Probe `GET /health`; a healthy process returns `{"status":"healthy"}`.
- Keep application and reverse-proxy logs in access-controlled centralized storage.
- Alert on repeated authentication failures, health-check failures, database write errors, abnormal process restarts, and storage exhaustion.
- Define retention and deletion rules before storing plate numbers or user data.

The included health check confirms that the web process responds. It does not verify hardware, external identity, or payment systems.

## 6. Back up and restore SQLite

Create a transactionally consistent backup:

```bash
uv run python scripts/backup_sqlite.py --output-dir backups
```

For Docker, run the command inside the service and copy the resulting backup to separately protected storage. Test restoration on a non-production instance. The script verifies SQLite integrity but cannot validate whether the backup meets an organization's recovery-time or retention requirements.

## 7. Schema changes

The current application creates missing tables through SQLAlchemy metadata. Before reusing it for a long-lived deployment, adopt reviewed schema migrations, take a verified backup before each change, and test both upgrade and recovery paths. Do not point a new release at the only copy of a production database.

## 8. Site integration checklist

- Map user identity and administrator roles to site policy.
- Threat-model exposed endpoints and terminate TLS at a maintained reverse proxy.
- Validate space-assignment rules against the physical layout and accessibility requirements.
- Add audit events appropriate to the operator workflow without logging secrets.
- Test camera, barrier, plate-recognition, and payment failure modes if those systems are integrated.
- Document data ownership, consent or other legal basis, retention, deletion, breach response, backup custody, and restore responsibility.
- Run a controlled pilot and record defects before broad use.

## 9. GitHub Pages

The `project-intro/` directory is a self-contained English static page. In GitHub, open **Settings → Pages**, select **GitHub Actions** as the source, and run the `Deploy project page` workflow. The workflow deploys only the static presentation assets; it does not host the FastAPI application or expose a database.
