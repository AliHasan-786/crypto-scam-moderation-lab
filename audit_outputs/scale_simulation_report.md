# Scale Simulation — Thresholds as Staffing Decisions

50,000 posts/day (scored sample: 6,000) · true prevalence 1.55% · generated 2026-07-04

| Review threshold | Queue/day | Review-net recall | Reviewers | Daily cost | Cost per caught scam |
| --- | --- | --- | --- | --- | --- |
| 0.25 | 47,666 | 100.0% | 199 | $45,372 | $59 |
| 0.30 | 33,366 | 100.0% | 140 | $31,920 | $41 |
| 0.35 | 19,283 | 100.0% | 81 | $18,468 | $24 |
| 0.40 | 8,833 | 100.0% | 37 | $8,436 | $11 |
| 0.45 | 6,341 | 100.0% | 27 | $6,156 | $8 |
| 0.50 | 5,666 | 100.0% | 24 | $5,472 | $7 |
| 0.55 | 4,033 | 90.3% | 17 | $3,876 | $6 |
| 0.60 | 2,883 | 77.4% | 13 | $2,964 | $5 |

The sweep makes Decision Log 002 concrete: dropping the review threshold from 0.40 to 0.30 buys ~1 point of review-net recall and roughly doubles reviewer payroll. The campaign weeks in the series show the real staffing problem is burst capacity, not steady state — which is why the incident runbook exists and why campaign-level clustering beats per-post scoring during waves.
