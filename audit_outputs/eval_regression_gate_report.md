# Trust & Safety Regression Gate

Generated: `2026-07-04T02:16:53.024886+00:00`

Overall result: **PASS**

- Checks: **11**
- Failed checks: **0**

## Checks

- **PASS** `scenario expectation pass rate`: 1.0 >= 1.0
- **PASS** `scenario public-label precision`: 1.0 >= 0.95
- **PASS** `scenario review-or-label recall`: 1.0 >= 1.0
- **PASS** `hardening expectation pass rate`: 1.0 >= 1.0
- **PASS** `hardening legitimate no-public-label rate`: 1.0 >= 1.0
- **PASS** `adversarial review-or-label retention`: 1.0 >= 1.0
- **PASS** `adversarial escape rate`: 0.0 <= 0.0
- **PASS** `evidence span faithfulness`: 1.0 >= 1.0
- **PASS** `ops review coverage demo floor`: 0.6 >= 0.5
- **PASS** `calibration case count`: 12.0 >= 12
- **PASS** `incident tabletop scenario count`: 3.0 >= 3

## Why This Gate Exists

This gate protects false-positive control, review routing, evidence faithfulness, calibration coverage, and incident readiness.
