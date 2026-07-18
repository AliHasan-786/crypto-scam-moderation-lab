# Structured Evidence Extractor Report

Generated: 2026-07-18T03:35:02.754589+00:00

## Summary

- Cases: 19
- Expectation pass rate: 100.0%
- Span faithfulness: 100.0%
- Fraud evidence recall: 100.0%
- Legitimate no-public-label rate: 100.0%
- Ambiguous review rate: 100.0%

Interpretation: this is a reviewer-assistance layer. It extracts cited evidence and recommended review posture, but it does not publish labels or override the classifier/policy pipeline.

## Action Counts

- human_review: 5
- no_action: 6
- public_label_candidate: 8

## Top Failures

No expectation failures.

## Design Notes

- Evidence spans must point back to source text.
- Public labels remain gated by the existing policy/model system.
- Hosted LLM output should be evaluated against this same schema before being exposed to reviewers.
- The next production step is a provider adapter plus regression tests for hallucinated evidence and over-enforcement.
