# Structured Evidence Extractor

Reviewer-assistance layer for the Crypto Scam Moderation Lab.

This module defines how a future hosted LLM should extract evidence for Trust & Safety reviewers without becoming the enforcement authority. The current implementation is deterministic so the schema, evals, and UI can be tested reproducibly before provider-specific LLM behavior is introduced.

## Files

- `evidence_schema.json`: JSON Schema for structured reviewer evidence.
- `prompts/evidence_extractor_system.md`: prompt contract for a future hosted LLM adapter.
- `structured_evidence_extractor.py`: local deterministic implementation and eval runner.

## Extracted Fields

- `promised_return`
- `transfer_ask`
- `wallet_connection_ask`
- `impersonated_entity`
- `urgency`
- `risky_link_or_wallet`
- `recovery_claim`
- `private_channel_or_signal`
- `benign_context`
- `missing_context`

The extractor returns one of three reviewer postures:

- `public_label_candidate`
- `human_review`
- `no_action`

This is not a final enforcement decision. It is structured evidence for reviewer workflow and downstream evals.

## Run

```bash
python3 llm_evidence/structured_evidence_extractor.py \
  --cases evals/scenario_eval_cases.json \
  --out audit_outputs/llm_evidence_report.json \
  --markdown-out audit_outputs/llm_evidence_report.md \
  --lab-summary crypto-scam-lab/data/evidenceSummary.js
```

## Current Metrics

- 19 authored scenario cases.
- 100.0% expectation pass rate.
- 100.0% span faithfulness.
- 100.0% fraud evidence recall.
- 100.0% legitimate no-public-label rate.
- 100.0% ambiguous review rate.

## Design Principle

Every evidence field must be backed by source spans. Warnings, research, satire, developer debugging, and skeptical help-seeking suppress public-label recommendations. Missing source, cropped link, OCR, or ambiguous intent routes to human review.

