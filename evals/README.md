# Evaluation Suite

This folder is the first portfolio-grade eval layer for the crypto scam moderation project.

## Why This Exists

The coursework model reported aggregate classification metrics. The portfolio project needs a stronger evaluation program that tests the decisions a Trust & Safety team actually makes:

- Which scam posts should receive a public label?
- Which uncertain posts should be routed to human review?
- Which legitimate posts must avoid public labeling?
- How does the model handle obfuscation?
- How does the policy layer handle production-hardening cases such as defanged URLs, shorteners, OCR ambiguity, Spanish-language phrasing, and protected-context false positives?
- Which scenario buckets fail?

## Run

```bash
python3 evals/crypto_scam_eval_suite.py \
  --cases evals/scenario_eval_cases.json \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --out audit_outputs/eval_suite_report.json \
  --lab-summary crypto-scam-lab/data/evalSummary.js
```

Run the production-hardening eval suite:

```bash
python3 evals/production_hardening_eval.py \
  --cases evals/hardening_eval_cases.json \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --out audit_outputs/production_hardening_eval_report.json \
  --markdown-out audit_outputs/production_hardening_eval_report.md \
  --lab-summary crypto-scam-lab/data/hardeningSummary.js
```

## Outputs

- `audit_outputs/eval_suite_report.json`: full reproducible eval report.
- `audit_outputs/production_hardening_eval_report.json`: full hardening eval report.
- `audit_outputs/production_hardening_eval_report.md`: interview-friendly hardening report.
- `crypto-scam-lab/data/evalSummary.js`: compact browser-lab summary.
- `crypto-scam-lab/data/hardeningSummary.js`: compact browser-lab hardening summary.

For the deeper Phase 4 red-team mutation workflow, use `../adversarial_lab/scam_mutation_lab.py`. That suite focuses on adversarial scam variants, downgrade rates, escapes, and an interview-ready Markdown report.

## Eval Design

The suite separates:

- Ground truth: fraud, legitimate, ambiguous.
- Operational action: no label, human review, public label, high-confidence escalation.
- Public-label safety: whether a public label is allowed.
- Review routing: whether the system should send the item to a reviewer.

This distinction is intentional. In Trust & Safety, the right product behavior is often not "classify harder." It is "route uncertainty to the right surface."
