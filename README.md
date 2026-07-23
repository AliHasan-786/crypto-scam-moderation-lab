# Crypto Scam Moderation Lab

**A working Trust & Safety system that publishes its own failures.**

An interactive moderation workbench for crypto investment scams on Bluesky-style platforms — built solo from Cornell Tech T&S coursework (CS 5342) into a full-stack safety system: written policy, tiered enforcement, human review, QA calibration, campaign intelligence, incident response, appeals, transparency reporting, an LLM-assist track, scale economics, and a CI release gate that regenerates every artifact on every commit.

**Live lab:** [crypto-scam-lab.vercel.app](https://crypto-scam-lab.vercel.app) — start with the story, try the decision boundary, or go straight to [what the system gets wrong](https://crypto-scam-lab.vercel.app/#failures).

---

## The problem

Investment scams cost Americans $5.8B in reported losses in 2024 (FBI IC3) — and the same words scammers use appear in warnings, news, satire, research, and victims asking for help. A system that just "catches scams" silences all of them. This project treats that boundary as the product: public labels require strong evidence, uncertainty routes to humans, protected speech suppresses enforcement, and every decision is explainable and appealable.

## What makes it different

**Failures are published, not hidden.** Authored eval suites that pass 100% prove nothing. The standing [error analysis](audit_outputs/error_analysis_report.md) shows the 8 real false positives at the operating point (with category commentary), and 5 authored hard cases the system still fails — kept on display until solved, then replaced with harder ones. Protected-context guard cases are the only ones the release gate enforces.

**Thresholds are treated as staffing decisions.** The [scale simulation](audit_outputs/scale_simulation_report.md) prices every threshold at 50,000 posts/day: queue load, reviewers required, cost per caught scam, and a 12-week series with campaign waves. Moving the review threshold from 0.40 to 0.30 roughly doubles payroll for ~1 point of recall — that tradeoff is Decision Log entry 002, not a footnote.

**The LLM earns its place or it doesn't.** A [hosted-LLM evidence adapter](llm_evidence/llm_adapter.py) runs against the same policy prompt and the same span-faithfulness gate as the deterministic extractor, with an honest [baseline-vs-LLM comparison](audit_outputs/llm_adapter_report.md) covering accuracy, cost, and latency. Public demo uses cached, provenance-labeled outputs; a regeneration script reruns them live.

**Live measurement stays bounded.** The optional radar in [Try it](https://crypto-scam-lab.vercel.app/#tester) connects a visitor's browser directly to the public Bluesky Jetstream relay and shows aggregate local routing counts only. It has a 10-minute/5,000-post cap, stores no live records, and cannot act on accounts. The accompanying calibration snapshot is explicitly EN/ES-screened routing load, not fraud prevalence or model performance.

**Operating-service work is gated.** The [shadow-service brief](docs/SHADOW_SERVICE_GATE_BRIEF.md) distinguishes build-only controls from private observation. The current [fixture-only harness](labeler_service/shadow_daemon.py) has kill-switch, rate-cap, and zero-outbound-write tests, but does not connect to a relay or publish labels. The first [hosted guard-model result](audit_outputs/external_guard_model_benchmark.md) is published with its [provenance](model_comparison/EXTERNAL_RUN_PROVENANCE.md); a [v2 shared-action preregistration](model_comparison/PREREGISTRATION_V2_SHARED_ACTIONS.md) fixes the mapping asymmetry before any further calls. The [reviewer-assistant red-team record](audit_outputs/reviewer_assist_red_team.md) keeps its protected-context failure visible.

**Policy is written like policy.** A platform-style [policy document](policy/CRYPTO_INVESTMENT_SCAM_POLICY.md), an [enforcement matrix](policy/ENFORCEMENT_MATRIX.md) (violation × severity × evidence × action), a dated [decision log](policy/DECISION_LOG.md) recording every tradeoff, [metrics definitions](ops_analytics/METRICS_DEFINITIONS.md) with failure modes for each number, and a [DSA statement-of-reasons sample](governance/dsa_statement_of_reasons_sample.json) mapping system outputs to EU transparency requirements.

**Grounded in documented fraud.** The [threat landscape](threat_landscape/THREAT_LANDSCAPE.md) maps every violation subtype to typologies documented by FBI IC3, Chainalysis, and the FTC — including what the highest-loss typology (pig butchering) makes invisible to single-post classification, and why that limit shapes the roadmap.

## The T&S stack, end to end

| Discipline | Where it lives |
| --- | --- |
| Policy development & taxonomy design | `policy/` — policy doc, enforcement matrix, decision log |
| Detection & ML | `policy_proposal_labeler_v2.py` — audited, reproducible baseline (original coursework model kept with its [audit](audit_outputs/original_labeler_audit.json)) |
| Evals & red-teaming | `evals/`, `adversarial_lab/` — scenario, hardening, mutation, regression gate, standing error analysis |
| LLM safety & assistance | `llm_evidence/`, GenAI abuse lab — evidence extraction, faithfulness gating, prompt-injection/tool-misuse tests |
| Human review & quality | `quality/` — calibration cases, answer keys, reviewer QA workflow |
| Operations & analytics | `ops_analytics/`, `scale_sim/` — SQL query pack, metrics definitions, capacity economics |
| Threat intelligence | `bluesky_integration/`, `threat_landscape/` — entity extraction, campaign graphing, typology grounding |
| Incident response | `incident_response/` — severity model, runbook, tabletop scenarios |
| Governance & compliance | `governance/` — appeals, reversals, notices, transparency report, Santa Clara / NIST mapping, DSA sample |
| Product & interface | `crypto-scam-lab/` — an interactive case study with a policy narrative, decision studio, published failures, and a full-system appendix |

## Current numbers (regenerated by CI on every commit)

Baseline test set: precision 0.882 / recall 1.000 / F1 0.938 (TN 100, FP 8, FN 0, TP 60) — with all 8 false positives [published and categorized](audit_outputs/error_analysis_report.md). Review-or-label retention under 56 controlled mutations: 100% (public-label retention 82.1% — downgrade-to-review under obfuscation is designed behavior, Decision Log 007). Evidence span faithfulness: 100% for both deterministic and LLM extractors. Scale model at 50k posts/day: ~18 reviewers at the operating point, with the full threshold-to-payroll sweep in the report. Launch gate: 15-step pipeline, guard cases enforced, unsolved failures deliberately not gated.

## Reproduce everything

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements-v2.txt
bash scripts/run_all_checks.sh   # same command CI runs
```

This retrains the baseline and regenerates every eval report, the error analysis, the LLM comparison, the scale simulation, governance/ops/calibration/incident artifacts, and all frontend data modules — failing if the release gate detects a regression.

Run the lab locally:

```bash
cd crypto-scam-lab && python3 -m http.server 5177
```

## Boundaries, stated plainly

The public demo is static and sanitized: it cannot publish labels, report accounts, resolve live links, or take any platform action. Live Bluesky ingestion is local, read-only, and opt-in. LLM output is reviewer assistance only, cached for the demo, and gated by faithfulness checks. The dataset is small and mostly English. The eval suites are authored — which is exactly why the error-analysis surface exists. Full limitations in the [case study](case_study/CRYPTO_SCAM_MODERATION_CASE_STUDY.md).
