# Governance, Appeals, And Transparency

Phase 6 turns the moderation demo into a more complete Trust & Safety operation surface.

This module generates transparency artifacts from two sources:

- the local SQLite review queue at `audit_outputs/live_review_queue.sqlite`
- sanitized authored appeal scenarios in `governance/appeal_scenarios.json`

The separation is intentional. Queue metrics reflect the local operational demo, while appeal scenarios exercise notice, appeal, reversal, and false-positive taxonomy flows without exposing live platform users.

## Files

- `appeal_scenarios.json`: authored appeal and reversal scenarios.
- `transparency_report.py`: report generator for JSON, Markdown, and browser-lab data.

## Run

```bash
python3 governance/transparency_report.py \
  --db audit_outputs/live_review_queue.sqlite \
  --scenarios governance/appeal_scenarios.json \
  --out audit_outputs/governance_transparency_report.json \
  --markdown-out audit_outputs/governance_transparency_report.md \
  --lab-summary crypto-scam-lab/data/governanceReport.js
```

## Current Snapshot

- 5 local queue candidates.
- 3 reviewed or triaged queue items.
- 1 locally actioned item.
- 4 authored appeal scenarios.
- 2 authored reversals.
- 50.0% authored appeal reversal rate.
- 0.914 standards scorecard average.

## What This Demonstrates

- Notice copy for labels, escalations, appeals, and reversals.
- Appeal flows for warning, satire, wallet-drainer, and ambiguous recovery-service cases.
- Reversal tracking and false-positive category reporting.
- Automation-assisted reporting without hiding human review.
- Standards mapping across Santa Clara Principles, NIST AI RMF, NIST CSF, OWASP LLM/Agentic AI, and local T&S operations.

