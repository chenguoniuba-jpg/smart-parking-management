# Security policy

This repository contains the public reusable edition of a system in actual use in Shanghai. Every new deployment must complete an environment-specific security review before exposing services to a public network or processing personal data.

## Reporting a vulnerability

Use GitHub's private security-advisory feature when available. Do not publish credentials, personal data or an exploitable proof of concept in a public issue.

## Deployment requirements

- Set `APP_ENV=production` and provide a random `SECRET_KEY` of at least 32 characters.
- Configure `CORS_ORIGINS` with the exact trusted origins.
- Replace SQLite with an appropriately managed database when concurrent production writes are required.
- Put the service behind HTTPS and a maintained reverse proxy.
- Add rate limiting, audit logging, backup, monitoring and dependency scanning.
- Never use demonstration users, generated credentials or real license-plate data in public examples.

Only the `/health`, login and static-interface routes are intentionally public. Management APIs require a valid administrator token; new administrators can be created only by a superuser.
