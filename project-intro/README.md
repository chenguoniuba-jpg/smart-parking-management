# Smart Parking Management System — English Case Study

[Back to the repository home](../README.md) · [Maintainer role](../MAINTAINER_ROLE.md) · [Deployment scope](../DEPLOYMENT.md) · [Standalone HTML presentation](project-intro.html)

## At a glance

| Item | Current public statement |
|---|---|
| Operational use began | March 2026 |
| Setting | Corporate industrial park parking facility in Shanghai |
| Operational scale | 3 administrators and 286 parking spaces |
| Iteration | Continued after launch; August v7 builds on the July v6 baseline |
| Public/on-site code relationship | Current public and current on-site application source match as of this snapshot |
| Verification boundary | The park management office can confirm use; private identities, credentials, and live records are excluded |

## The problem

Industrial-park parking combines long-duration occupancy, peak-hour demand, accessibility needs, reservation handling, and operator follow-up. The project converts those operational concerns into a small management system with inspectable rules instead of presenting a black-box optimization claim.

## The system

- A FastAPI backend exposes authenticated management APIs.
- SQLAlchemy models users, administrators, spaces, parking records, reservations, points, credit events, configuration, and traffic baselines.
- A vanilla JavaScript interface supports daily administrator workflows.
- Space assignment scores size compatibility, accessibility needs, and floor preference.
- Traffic estimates summarize historical hourly entries deterministically; they are not a trained machine-learning model.
- Automated tests cover authentication, assignment, parking entry and exit, reservations, configuration, baseline behavior, and backup tooling.

## Operational timeline

1. **January–March 2026:** early requirements and design records.
2. **March 2026:** operational use began in the Shanghai industrial park.
3. **April–July 2026:** the running system continued through implementation and interface iterations.
4. **August 2026:** v7 aligned the July baseline with the current implementation, evidence boundaries, security work, automated tests, and public-reuse packaging.

March is the launch date; August is the current public-release iteration. The current-code relationship does not mean the August snapshot existed unchanged in March.

## What the maintainer did in this public release

The current public package supports a concrete statement about release stewardship: the maintainer supplied and confirmed the operational scope, set the public/private data boundary, preserved the iteration chain, required implementation claims to be corrected, separated sample and live data, and reviewed the repository for public reuse.

See [Maintainer role and attribution](../MAINTAINER_ROLE.md) for the evidence map and the boundary between documented stewardship and technical-authorship claims that still require personal confirmation.

## Public evidence boundary

The 286-space capacity is a maintainer-confirmed site fact. The public dashboard is visibly marked “公开示例数据”; its other counts and percentages are presentation data, not published live-site metrics. The repository does not claim a measured efficiency improvement, validated prediction accuracy, or a reproducible performance benchmark without separately authorized evidence.

## Explore

- [Run and reuse the system](../REUSE.md)
- [Review evidence and limitations](../EVIDENCE_AND_LIMITATIONS.md)
- [Read the public release note](../PUBLIC_RELEASE.md)
- [Open the standalone visual presentation](project-intro.html)

After the repository is uploaded and GitHub Pages is enabled, the standalone presentation can be published by the included `Deploy project page` workflow.
