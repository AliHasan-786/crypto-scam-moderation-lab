# Crypto Scam Moderation Lab

Interactive Trust & Safety workbench built from the CS 5342 Bluesky labeler project.

**Live lab:** [crypto-scam-lab.vercel.app](https://crypto-scam-lab.vercel.app)

## What This Adds

- Editorial case-study shell with four primary destinations: the story, decision studio, published failures, and a full-system appendix.
- First-screen overview with the background problem, a five-part Assignment 2 policy brief, policy-to-product build path, static decision-flow preview, and concise terminology.
- Reviewer queue over the existing train/test posts.
- Explainable policy-rubric score for crypto scam indicators.
- Live threshold tuning with precision, recall, F1, and confusion matrix.
- Eval-suite summary for scenario coverage, adversarial variants, and public-label precision.
- Hardening eval summary for canonicalization, URL evidence, OCR/source ambiguity, Spanish-language cases, and protected-context false positives.
- Ops analytics panel for queue health, review coverage, backlog, action distribution, false-positive candidates, and entity leads.
- Interactive 12-case QA calibration simulator with action accuracy and over/under-enforcement feedback.
- Interactive incident replay with response choices, consequence meters, tabletop context, and generated follow-up.
- Launch gate panel for portfolio-level regression checks across evals, ops, calibration, incident readiness, evidence, and governance.
- Adversarial lab summary for controlled mutation robustness, downgrades, and escapes.
- GenAI abuse lab for deterministic synthetic variants and assistant-boundary tests.
- Evidence extractor summary for cited reviewer evidence, faithfulness, overreach, and action distribution.
- Governance panel for notice copy, authored appeal flows, reversal tracking, transparency metrics, and standards controls.
- Live review-store import from the local SQLite queue.
- Campaign graph and public-safe gallery for shared domains, wallets, recovery scams, fake support, warning false positives, and OCR ambiguity.
- Entity chips inside live case review.
- Custom post tester with scam, legitimate, ambiguous, satire, and adversarial mutation controls.
- ABC-style intervention panel for content, behavior, and actor-level responses.
- Reported Python model summary using the v2 evaluation and an inline baseline chart.

The browser scorer is intentionally an explainable policy simulator. The original
coursework ML implementation remains `../policy_proposal_labeler.py`, while the
portfolio baseline is `../policy_proposal_labeler_v2.py`.

## Run Locally

From this folder:

```bash
python3 -m http.server 5177
```

Then open:

```text
http://127.0.0.1:5177
```

## Refresh Demo Data

If `../data.csv` or `../test.csv` changes, regenerate the public data module:

```bash
python3 scripts/generate_posts_module.py
```

## Refresh Eval Summary

If `../evals/scenario_eval_cases.json` or the v2 model changes, regenerate the eval report and browser summary:

```bash
python3 ../evals/crypto_scam_eval_suite.py \
  --cases ../evals/scenario_eval_cases.json \
  --model-path ../audit_outputs/fraud_labeler_v2.joblib \
  --out ../audit_outputs/eval_suite_report.json \
  --lab-summary data/evalSummary.js
```

## Refresh Hardening Evals

If canonicalization rules, URL evidence, hardening cases, or the v2 model changes:

```bash
python3 ../evals/production_hardening_eval.py \
  --cases ../evals/hardening_eval_cases.json \
  --model-path ../audit_outputs/fraud_labeler_v2.joblib \
  --out ../audit_outputs/production_hardening_eval_report.json \
  --markdown-out ../audit_outputs/production_hardening_eval_report.md \
  --lab-summary data/hardeningSummary.js
```

## Refresh Adversarial Lab

If the model, scenario cases, or mutation operators change:

```bash
python3 ../adversarial_lab/scam_mutation_lab.py \
  --cases ../evals/scenario_eval_cases.json \
  --model-path ../audit_outputs/fraud_labeler_v2.joblib \
  --out ../audit_outputs/adversarial_scam_lab_report.json \
  --markdown-out ../audit_outputs/adversarial_scam_lab_report.md \
  --lab-summary data/adversarialLab.js
```

## Refresh Evidence Extractor

If the scenario cases, evidence schema, or prompt contract changes:

```bash
python3 ../llm_evidence/structured_evidence_extractor.py \
  --cases ../evals/scenario_eval_cases.json \
  --out ../audit_outputs/llm_evidence_report.json \
  --markdown-out ../audit_outputs/llm_evidence_report.md \
  --lab-summary data/evidenceSummary.js
```

## Refresh Governance Report

If the local queue or appeal scenarios change:

```bash
python3 ../governance/transparency_report.py \
  --db ../audit_outputs/live_review_queue.sqlite \
  --scenarios ../governance/appeal_scenarios.json \
  --out ../audit_outputs/governance_transparency_report.json \
  --markdown-out ../audit_outputs/governance_transparency_report.md \
  --lab-summary data/governanceReport.js
```

## Refresh Ops Analytics

```bash
python3 ../ops_analytics/generate_ops_report.py \
  --db ../audit_outputs/live_review_queue.sqlite \
  --out ../audit_outputs/ops_analytics_report.json \
  --markdown-out ../audit_outputs/ops_analytics_report.md \
  --lab-summary data/opsAnalytics.js
```

## Refresh Reviewer Calibration

```bash
python3 ../quality/reviewer_calibration.py \
  --cases ../quality/calibration_cases.json \
  --out ../audit_outputs/reviewer_calibration_report.json \
  --markdown-out ../audit_outputs/reviewer_calibration_report.md \
  --lab-summary data/qualityCalibration.js
```

## Refresh Incident Response

```bash
python3 ../incident_response/incident_tabletop.py \
  --scenarios ../incident_response/incident_scenarios.json \
  --out ../audit_outputs/incident_response_tabletop.json \
  --markdown-out ../audit_outputs/incident_response_tabletop.md \
  --lab-summary data/incidentResponse.js
```

## Refresh Launch Gate

```bash
python3 ../evals/eval_regression_gate.py \
  --out ../audit_outputs/eval_regression_gate_report.json \
  --markdown-out ../audit_outputs/eval_regression_gate_report.md \
  --lab-summary data/evalGate.js
```

## Refresh Live Review Queue

If the local SQLite queue changes, export it into the static lab:

```bash
python3 ../bluesky_integration/review_queue_cli.py \
  --db ../audit_outputs/live_review_queue.sqlite \
  export \
  --out data/liveReviewQueue.js
```

The included demo queue is sanitized and marked as `source = demo`. Real Bluesky ingestion remains local-only until you explicitly run search or Jetstream with the `--db` flag.

## Refresh Campaign Graph

If the local SQLite queue changes and you want to refresh shared-entity/campaign evidence:

```bash
python3 ../bluesky_integration/review_queue_cli.py \
  --db ../audit_outputs/live_review_queue.sqlite \
  graph \
  --out ../audit_outputs/campaign_graph.json \
  --lab-summary data/campaignGraph.js
```

## Data Provenance

`data/posts.js` is generated from the assignment CSV files:

- `../data.csv`
- `../test.csv`

These posts are used only for public-safe demo/evaluation interactions.

`data/liveReviewQueue.js` is exported from the local SQLite review queue. The current checked-in queue contains sanitized demo items, not live Bluesky user content.

`data/campaignGraph.js` is generated from the same local SQLite queue and summarizes deterministic entity links. The included graph contains a synthetic repeated-domain/reused-wallet campaign for demonstration.

`data/adversarialLab.js` is generated from the controlled red-team mutation suite. It contains summarized robustness results, not live platform content.

`data/hardeningSummary.js` is generated from the production-hardening eval suite. It summarizes canonicalization, URL evidence, OCR ambiguity, multilingual, review-routing, and false-positive controls.

`data/evidenceSummary.js` is generated from the structured evidence extractor. It contains summarized reviewer-assistance eval results and compact examples, not live platform content.

`data/governanceReport.js` is generated from the governance/transparency report. It combines local queue metrics with sanitized authored appeal scenarios for notice, appeal, and reversal flows.
