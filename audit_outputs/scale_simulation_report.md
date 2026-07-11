# Scale Simulation — Thresholds as Staffing Decisions

50,000 posts/day (scored sample: 6,000) · true prevalence 1.55% · generated 2026-07-11

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

## At 5,000,000 posts/day (mid-size platform)

Same measured rates, production volume. Surge = campaign-wave weeks (3x queue).

| Review threshold | Queue/day | Reviewers | Surge reviewers | Annual review cost |
| --- | --- | --- | --- | --- |
| 0.25 | 4,766,500 | 19,861 | 59,582 | $1,652,832,420 |
| 0.30 | 3,336,500 | 13,903 | 41,707 | $1,157,007,660 |
| 0.35 | 1,928,500 | 8,036 | 24,107 | $668,755,920 |
| 0.40 | 883,500 | 3,682 | 11,044 | $306,416,040 |
| 0.45 | 634,000 | 2,642 | 7,925 | $219,867,240 |
| 0.50 | 566,500 | 2,361 | 7,082 | $196,482,420 |
| 0.55 | 403,499 | 1,682 | 5,044 | $139,976,040 |
| 0.60 | 288,500 | 1,203 | 3,607 | $100,113,660 |

At this volume the sweep stops being a staffing question and becomes an architecture question: no threshold shift closes a multi-hundred-reviewer surge gap, which is why the 100x roadmap moves detection to campaign-level clustering and reserves per-post review for the measurement slice.

## Reality check against the live firehose

The same model and decision layer, run over 8,210 real posts from the public Bluesky Jetstream firehose (2026-07-11 22:34Z), measured a review-tier share of 7.10% against the synthetic corpus share of 16.25%. Measured on real firehose traffic with the same model and decision layer. The gap between the synthetic corpus share and the live share is the calibration error this report would otherwise hide; live-traffic staffing should be read from the measured share.

The sweep makes Decision Log 002 concrete: dropping the review threshold from 0.40 to 0.30 buys ~1 point of review-net recall and roughly doubles reviewer payroll. The campaign weeks in the series show the real staffing problem is burst capacity, not steady state — which is why the incident runbook exists and why campaign-level clustering beats per-post scoring during waves.
