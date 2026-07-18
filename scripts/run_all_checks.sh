#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

echo "[preflight] Validating versioned evaluation inputs"
"$PYTHON_BIN" evals/validate_manifest.py

echo "[1/15] Auditing the original labeler"
"$PYTHON_BIN" audit_original_labeler.py > audit_outputs/original_labeler_audit.json

echo "[2/15] Training and evaluating the reproducible baseline"
"$PYTHON_BIN" policy_proposal_labeler_v2.py evaluate \
  --train data.csv \
  --test test.csv \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --out audit_outputs/v2_evaluation.json > /dev/null

echo "[3/15] Running scenario and adversarial evals"
"$PYTHON_BIN" evals/crypto_scam_eval_suite.py \
  --cases evals/scenario_eval_cases.json \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --out audit_outputs/eval_suite_report.json \
  --lab-summary crypto-scam-lab/data/evalSummary.js

echo "[4/15] Running production-hardening evals"
"$PYTHON_BIN" evals/production_hardening_eval.py \
  --cases evals/hardening_eval_cases.json \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --out audit_outputs/production_hardening_eval_report.json \
  --markdown-out audit_outputs/production_hardening_eval_report.md \
  --lab-summary crypto-scam-lab/data/hardeningSummary.js

echo "[5/15] Running controlled mutation tests"
"$PYTHON_BIN" adversarial_lab/scam_mutation_lab.py \
  --cases evals/scenario_eval_cases.json \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --out audit_outputs/adversarial_scam_lab_report.json \
  --markdown-out audit_outputs/adversarial_scam_lab_report.md \
  --lab-summary crypto-scam-lab/data/adversarialLab.js

echo "[6/15] Checking evidence extraction"
"$PYTHON_BIN" llm_evidence/structured_evidence_extractor.py \
  --cases evals/scenario_eval_cases.json \
  --out audit_outputs/llm_evidence_report.json \
  --markdown-out audit_outputs/llm_evidence_report.md \
  --lab-summary crypto-scam-lab/data/evidenceSummary.js

echo "[7/15] Generating governance and transparency metrics"
"$PYTHON_BIN" governance/transparency_report.py \
  --db audit_outputs/live_review_queue.sqlite \
  --scenarios governance/appeal_scenarios.json \
  --out audit_outputs/governance_transparency_report.json \
  --markdown-out audit_outputs/governance_transparency_report.md \
  --lab-summary crypto-scam-lab/data/governanceReport.js

echo "[8/15] Generating operations analytics"
"$PYTHON_BIN" ops_analytics/generate_ops_report.py \
  --db audit_outputs/live_review_queue.sqlite \
  --out audit_outputs/ops_analytics_report.json \
  --markdown-out audit_outputs/ops_analytics_report.md \
  --lab-summary crypto-scam-lab/data/opsAnalytics.js

echo "[9/15] Running reviewer calibration"
"$PYTHON_BIN" quality/reviewer_calibration.py \
  --cases quality/calibration_cases.json \
  --out audit_outputs/reviewer_calibration_report.json \
  --markdown-out audit_outputs/reviewer_calibration_report.md \
  --lab-summary crypto-scam-lab/data/qualityCalibration.js

echo "[10/15] Running incident-response tabletop checks"
"$PYTHON_BIN" incident_response/incident_tabletop.py \
  --scenarios incident_response/incident_scenarios.json \
  --out audit_outputs/incident_response_tabletop.json \
  --markdown-out audit_outputs/incident_response_tabletop.md \
  --lab-summary crypto-scam-lab/data/incidentResponse.js

echo "[11/15] Refreshing campaign intelligence"
"$PYTHON_BIN" bluesky_integration/review_queue_cli.py \
  --db audit_outputs/live_review_queue.sqlite \
  graph \
  --out audit_outputs/campaign_graph.json \
  --lab-summary crypto-scam-lab/data/campaignGraph.js > /dev/null

echo "[12/15] Running standing error analysis (failures are published, guards enforced)"
"$PYTHON_BIN" evals/error_analysis.py \
  --test test.csv \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --unsolved evals/unsolved_cases.json \
  --out audit_outputs/error_analysis_report.json \
  --markdown-out audit_outputs/error_analysis_report.md \
  --lab-summary crypto-scam-lab/data/errorAnalysis.js

echo "[13/15] Comparing baseline vs cached LLM evidence adapter"
"$PYTHON_BIN" llm_evidence/llm_adapter.py \
  --cases evals/scenario_eval_cases.json \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --cache llm_evidence/cache/llm_evidence_cache.json \
  --out audit_outputs/llm_adapter_report.json \
  --markdown-out audit_outputs/llm_adapter_report.md \
  --lab-summary crypto-scam-lab/data/llmComparison.js

echo "[14/15] Running the scale and capacity simulation"
"$PYTHON_BIN" scale_sim/simulate_scale.py \
  --model-path audit_outputs/fraud_labeler_v2.joblib \
  --out audit_outputs/scale_simulation_report.json \
  --markdown-out audit_outputs/scale_simulation_report.md \
  --lab-summary crypto-scam-lab/data/scaleSimulation.js

echo "[15/15] Enforcing the release gate"
"$PYTHON_BIN" evals/eval_regression_gate.py \
  --out audit_outputs/eval_regression_gate_report.json \
  --markdown-out audit_outputs/eval_regression_gate_report.md \
  --lab-summary crypto-scam-lab/data/evalGate.js

echo "[provenance] Stamping generated reports with manifest and dataset hashes"
"$PYTHON_BIN" scripts/stamp_report_provenance.py

node --check crypto-scam-lab/app.js
"$PYTHON_BIN" -m compileall -q \
  adversarial_lab \
  bluesky_integration \
  evals \
  governance \
  incident_response \
  llm_evidence \
  ops_analytics \
  quality \
  audit_original_labeler.py \
  policy_proposal_labeler_v2.py

echo "All release checks passed."
