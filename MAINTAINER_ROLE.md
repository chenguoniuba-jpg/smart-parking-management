# Maintainer role and attribution

## Purpose

This statement answers a narrow question: what can the current public repository support about the maintainer's own role? It separates documented public-release stewardship from claims of sole authorship that a clean snapshot cannot independently prove.

## Documented role in the current public release

For the August 2026 public-reuse release, the repository maintainer:

- supplied and confirmed the operational scope: use began in March 2026 at a Shanghai corporate industrial park, with 3 administrators and 286 managed spaces;
- defined the privacy boundary that excludes the company identity, exact address, credentials, personal records, live database, and raw operational logs;
- preserved the design lineage from the July v6 baseline to the August v7 iteration instead of presenting the public snapshot as a new project;
- required public claims to be checked against the implementation, including the distinction between a deterministic traffic baseline and a trained machine-learning model;
- required public sample data to be visibly separated from private site data and confirmed that only the 286-space capacity is presented as a site figure in the dashboard example;
- reviewed the release package for reuse, including documentation, tests, locked dependencies, environment configuration, container packaging, backup tooling, and GitHub Pages preparation; and
- remains responsible for the accuracy of the published scope, attribution, and release decisions.

These responsibilities describe product direction, evidence discipline, and release stewardship. They do not by themselves prove who originally wrote every backend, frontend, or design artifact.

## Evidence map

| Responsibility | Repository evidence |
|---|---|
| Operational scope and privacy boundary | [`DEPLOYMENT.md`](DEPLOYMENT.md) |
| July-to-August iteration relationship | [`doc/product_mgt/README.md`](doc/product_mgt/README.md), [`doc/manual/CHANGELOG.md`](doc/manual/CHANGELOG.md) |
| Claims matched to implementation | [`EVIDENCE_AND_LIMITATIONS.md`](EVIDENCE_AND_LIMITATIONS.md), [`README.md`](README.md) |
| Public sample-data distinction | [`images/dashboard.png`](images/dashboard.png), [`backend/init_data.py`](backend/init_data.py) |
| Reuse and release preparation | [`REUSE.md`](REUSE.md), [`uv.lock`](uv.lock), [`.github/workflows/`](.github/workflows/) |

## What an applicant must still verify personally

Before an admissions application claims individual technical authorship, the applicant should confirm exactly which of the following they personally performed and can explain in an interview:

- problem discovery and conversations with parking administrators;
- requirements writing and the v1–v7 design decisions;
- database and API architecture;
- backend implementation;
- frontend implementation;
- rule design and validation;
- testing, debugging, deployment, and operator support;
- review or coordination of AI-assisted work.

Only verified items should be converted into a first-person applicant statement. Real commits, issue discussions, dated design notes, demo recordings, and an authorized confirmation letter are stronger evidence than file names or retrospective prose.

## AI assistance

AI tools assisted with selected review, refactoring, image labeling, documentation, and release packaging. The maintainer set the scope, supplied deployment facts, accepted or rejected claims, and remains accountable for the published result. AI assistance should not be represented as unaided personal coding.
