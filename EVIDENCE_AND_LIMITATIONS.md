# Evidence and limitations

## Repository history boundary

The system was completed before Git was introduced for public release. This repository therefore begins with the `v1.0.0` public-release snapshot and does not contain the original development commit history. The dated design files and changelog are retrospective historical design and iteration records; they can show documented changes in requirements and presentation, but they are not asserted to map to earlier Git commits. Repository activity after publication is recorded normally with real dates.

## Operational status

The project maintainer confirms that operational use began in March 2026 at a corporate industrial park parking facility in Shanghai. Three administrators use the system to manage 286 parking spaces, and all application modules included in the public edition are used on site. The system continued to be iterated after launch. As of the current public snapshot, the public repository and the on-site application use the same application source code; the statement does not mean the August snapshot existed unchanged in March. The corporate industrial park management office can confirm the operational use. See [DEPLOYMENT.md](DEPLOYMENT.md) for the stated scope and privacy boundary.

## What can be verified from this repository

- The source implements a FastAPI backend, a browser interface and a SQLite data model.
- Automated tests verify selected authentication, routing and parking-management behaviors.
- Seven design documents show multiple requirement and interface directions; v7 records the August public-release iteration based on the July v6 design.
- The initializer creates 286 clearly labeled example parking spaces, matching the confirmed on-site capacity while excluding live identifiers and records.

## What the public package does not include

- It does not publish Shanghai site identity, access credentials, personal user records or participant authorization forms.
- It does not publish raw Shanghai operational before-and-after data or a reproducible impact study.
- It does not establish forecast accuracy, sub-100 ms latency or support for a stated concurrent-user count.
- Dashboard screenshots and initialized records are public sample content, separate from live Shanghai operational data. The dashboard image is visibly marked “公开示例数据”; except for the confirmed 286-space capacity, displayed counts and percentages are not published as live site metrics.

## Current analytical method

The traffic component is a deterministic historical baseline. It counts recorded entries by hour, selects the most frequent hour and reports an average volume per observed day. The `confidence` field is a capped sample-coverage indicator retained for API compatibility; it is not a statistical confidence interval or calibrated model probability. With no historical records, the system returns zero volume and zero confidence.

The parking-space scheduler uses an inspectable score for size compatibility, accessibility needs and floor. This makes the decision reproducible, but it should be described as a rule-based heuristic rather than artificial intelligence or mathematical optimization.

## Publishing measured outcomes

Any public efficiency, usability or performance claim should be supported by authorized, privacy-preserving evidence. A suitable measurement package would define the question, sampling period, task or operational metric, calculation method, anonymization approach, raw-data retention policy and limitations before presenting results.
