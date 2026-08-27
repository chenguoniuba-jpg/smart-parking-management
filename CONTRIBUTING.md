# Contributing

Contributions are welcome for this open-source smart parking system.

1. Create a focused branch and explain the behavior being changed.
2. Keep examples free of real names, phone numbers, license plates, secrets and operational data.
3. Describe generated or demonstration data explicitly.
4. Do not add performance, usability or impact claims without a reproducible method and supporting evidence.
5. Run `uv sync --extra dev` and `uv run pytest` before opening a pull request.

Security reports should follow `SECURITY.md` rather than a public issue.

## Commit and release history

- Use the actual date and identity for every commit. Do not backdate commits or reconstruct a development history that did not exist in Git.
- Keep each commit focused on one real change. Suggested prefixes include `feat:`, `fix:`, `test:`, `docs:`, `refactor:` and `chore:`.
- Explain the behavior and verification in the commit or pull-request description when the reason is not obvious from the diff.
- Use version tags and GitHub Releases for published iterations; do not use retrospective design-document dates as tag or commit dates.
- Treat the repository's first commit and `v1.0.0` tag as the completed project's first public-release snapshot. All later work should be recorded prospectively.
