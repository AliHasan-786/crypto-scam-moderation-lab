# Metrics Definitions

Every number this project reports, with its computation, source artifact, and — most importantly — how it can mislead or be gamed. A metric without a documented failure mode is a metric waiting to be abused.

**Format:** definition · formula/source · failure modes.

---

## Decision-quality metrics

**Public-label precision** — Of posts the system would surface as public-label candidates, the share that are truly fraudulent. Primary guardrail metric: a wrong public label is a platform-inflicted harm.
*Source:* `audit_outputs/v2_evaluation.json` (`test_metrics.precision`, currently 0.882 at threshold 0.54).
*Failure modes:* inflated by easy negatives in the corpus; says nothing about the severity distribution of the FPs (labeling one journalist is worse than eight shitposts). Track FP categories in error analysis, not just the rate.

**Review-or-label recall** — Share of truly fraudulent posts that reached *any* human workflow (review, label candidate, or escalation). Primary safety-net metric.
*Source:* eval suite report; threshold tuning (`review` tier recall 0.9886 at the 0.40 policy floor).
*Failure modes:* can be driven to 1.0 trivially by flooding the queue — must always be read against review coverage and backlog. This pairing is the core capacity/safety tradeoff (Decision Log 002).

**Protected-context false-positive rate** — Share of protected-context cases (warnings, news, satire, research, debugging, help-seeking) that incorrectly receive a public-label candidate.
*Source:* protected-context slice of scenario + hardening eval reports.
*Failure modes:* the case set is authored; a 0% rate proves the *encoded* boundary holds, not that the boundary is complete. New reversal categories from appeals must feed new cases.

**Mutation retention** — Under controlled obfuscation, (a) share of scam variants still reaching review-or-label (must be 100%) and (b) share retaining the public label (82.1%; the gap is designed downgrade behavior, Decision Log 007).
*Source:* `audit_outputs/adversarial_scam_lab_report.json`.
*Failure modes:* mutation operators are the author's imagination of the adversary; retention against them is an upper bound on retention against real adversaries.

## Operational metrics

**Review coverage** — Reviewed items ÷ items queued for review, per period.
*Source:* `ops_analytics/generate_ops_report.py` from the SQLite review store.
*Failure modes:* coverage can be kept high by under-queuing (raising thresholds), which silently trades recall for a prettier ops number — read jointly with review-or-label recall.

**Backlog and time-to-action** — Open review items; and for each actioned item, time from ingestion to final decision (median and p95, not mean — the tail is where harm compounds, because scam posts do damage per hour of exposure).
*Source:* review store timestamps; surfaced in the ops report.
*Failure modes:* p95 hides per-severity differences; a production version splits SLA by severity tier (S1 target measured in minutes, S3 in days).

**Cost per decision** — Fully loaded reviewer minutes × loaded rate ÷ decisions, plus model inference cost per 1k posts. Introduced with the scale simulation (`scale_sim/`).
*Failure modes:* driving cost down rewards rubber-stamping; must be read against calibration agreement scores.

## Prevalence & transparency metrics

**Prevalence (modeled)** — Share of all posts in a surface that violate this policy, estimated from stratified sampling in the scale simulation (true rates are known there because the corpus is synthetic; in production this would be a labeled random sample, never a detection-derived number).
*Failure modes:* detection-based "prevalence" measures what you catch, not what exists — the single most common dishonest metric in transparency reporting. The simulation makes the distinction explicit.

**Actioned-content rate** — Actions per 10k posts, split by action type and detection source (proactive vs. reported).
*Source:* transparency report generator.
*Failure modes:* rises with both real enforcement and over-enforcement; meaningless without the appeal overturn rate beside it.

**Appeal overturn rate** — Reversals ÷ appeals decided, by reversal category.
*Source:* `audit_outputs/governance_transparency_report.json`.
*Failure modes:* a low rate can mean good decisions or a hostile appeal UX; report alongside appeal *submission* rate. Current sample is authored scenarios (n=4), stated wherever the number appears.

**Span faithfulness** — Share of extracted evidence claims backed by verbatim source spans. Applies equally to the deterministic extractor and the LLM adapter; it is the gate that keeps generated "evidence" honest.
*Source:* `audit_outputs/llm_evidence_report.json`.
*Failure modes:* verbatim quoting can still mislead by omission of exculpatory context; calibration cases include context-omission checks.

## Quality metrics

**Calibration agreement** — Reviewer agreement with the answer key on the 12-case calibration set, overall and on the 7 protected-context cases specifically.
*Source:* `audit_outputs/reviewer_calibration_report.json`.
*Failure modes:* answer keys encode the policy author's judgment; systematic reviewer disagreement on a case class is policy feedback, not reviewer error (that feedback loop is the point of QA).

**Launch-gate status** — Pass/fail across the release checks; any regression on the metrics above blocks merge via CI.
*Source:* `audit_outputs/eval_regression_gate_report.json`.
*Failure modes:* gates only protect encoded expectations. The error-analysis surface exists precisely because green gates are not evidence of absence of failure.
