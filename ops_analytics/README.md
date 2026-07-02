# Trust & Safety Ops Analytics

This folder turns the local review queue into PM / Analyst / Policy Ops signals.

The goal is not to prove model sophistication. The goal is to show that the moderation system can answer operational questions:

- How many items are waiting for review?
- Which actions create the most review load?
- Which cases are likely false positives?
- Which domains, wallets, handles, brands, or phrases repeat across cases?
- What evidence would a reviewer or policy lead need to improve the workflow?
- Is the system creating a useful feedback loop for policy and detection improvements?

## Run

```bash
python3 ops_analytics/generate_ops_report.py \
  --db audit_outputs/live_review_queue.sqlite \
  --out audit_outputs/ops_analytics_report.json \
  --markdown-out audit_outputs/ops_analytics_report.md \
  --lab-summary crypto-scam-lab/data/opsAnalytics.js
```

## Query Pack

`trust_safety_ops_queries.sql` contains standalone SQL queries that can be shown as role evidence for analyst, PM, and policy operations roles.
