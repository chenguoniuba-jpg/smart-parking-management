"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
import secrets
import warnings


APP_ENV = os.getenv("APP_ENV", "development").strip().lower()


def _load_secret_key() -> str:
    configured = os.getenv("SECRET_KEY", "").strip()
    if configured:
        if len(configured) < 32:
            raise RuntimeError("SECRET_KEY must contain at least 32 characters")
        return configured

    if APP_ENV in {"production", "prod"}:
        raise RuntimeError("SECRET_KEY is required when APP_ENV=production")

    warnings.warn(
        "SECRET_KEY is not set; using a temporary development key. "
        "Existing sessions will expire after restart.",
        RuntimeWarning,
        stacklevel=2,
    )
    return secrets.token_urlsafe(48)


SECRET_KEY = _load_secret_key()
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "8000"))

_origins = os.getenv(
    "CORS_ORIGINS",
    "http://127.0.0.1:8000,http://localhost:8000",
)
CORS_ORIGINS = [origin.strip() for origin in _origins.split(",") if origin.strip()]

if APP_ENV in {"production", "prod"} and "*" in CORS_ORIGINS:
    raise RuntimeError("Wildcard CORS origins are not allowed in production")
