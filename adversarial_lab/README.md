# Adversarial Scam Lab

Controlled red-team suite for the crypto scam moderation project.

## Purpose

Phase 4 tests whether the v2 labeler and operational policy survive realistic scammer adaptation:

- spaced keywords
- leetspeak
- punctuation stuffing
- defanged URLs
- brand shifts
- synonym laundering
- screenshot/OCR-style text
- support/eligibility context laundering

The goal is not to prove the model is perfect. The goal is to make failure modes visible and turn them into regression tests.

## Run

```bash
python3 adversarial_lab/scam_mutation_lab.py \
  --cases evals/scenario_eval_cases.json \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --out audit_outputs/adversarial_scam_lab_report.json \
  --markdown-out audit_outputs/adversarial_scam_lab_report.md \
  --lab-summary crypto-scam-lab/data/adversarialLab.js
```

If your default Python environment does not have the v2 dependencies:

```bash
python3 -m venv /tmp/crypto-scam-v2-venv
/tmp/crypto-scam-v2-venv/bin/python -m pip install -r requirements-v2.txt
/tmp/crypto-scam-v2-venv/bin/python adversarial_lab/scam_mutation_lab.py
```

## Outputs

- `audit_outputs/adversarial_scam_lab_report.json`: full machine-readable report.
- `audit_outputs/adversarial_scam_lab_report.md`: interview-friendly red-team report.
- `crypto-scam-lab/data/adversarialLab.js`: browser-lab summary.

## Metrics

- Public-label retention: mutated scam still receives a public label.
- Review-or-label retention: mutated scam is still caught by either review routing or public label.
- Downgrade rate: mutation moved an item to a lower action tier.
- Escape rate: mutation moved an item to `no_label`.
- Severe downgrade rate: mutation moved a public-label baseline to `no_label`.

For Trust & Safety, review-or-label retention is the recall-first safety metric. Public-label retention is stricter and should be interpreted with due-process constraints.
