# Crypto Scam Incident Tabletop Report

Generated: `2026-07-02T03:16:16.138531+00:00`

## Summary

- Scenarios: **3**
- Highest severity scenario: **Coordinated wallet-drainer airdrop campaign** (`sev2`)

## Operating Principles

- Preserve evidence before broad enforcement changes.
- Route ambiguity to review instead of forcing a public label.
- Use shared entities as campaign leads, not standalone proof.
- Convert incidents into eval, policy, QA, or tooling updates.
- Track false-positive impact alongside fraud mitigation.

## Scenario Details

### Coordinated wallet-drainer airdrop campaign

- ID: `ir_wallet_drainer_campaign`
- Severity: `sev2`
- Trigger: Multiple new accounts reuse the same defanged airdrop domain and wallet-connection language within a short window.

First actions:
- Freeze automatic public-enforcement expansion until evidence is reviewed
- Create campaign cluster and preserve entity evidence
- Route representative samples to senior reviewer
- Add temporary warning friction for repeated domain if policy evidence is confirmed

Mitigations:
- Domain-level warning friction
- Reviewer priority boost for shared-infrastructure posts
- Temporary rate limits on new accounts posting the repeated domain
- Add campaign examples to hardening evals and reviewer calibration

Success metrics:
- time to cluster confirmation
- review SLA for high-risk samples
- false-positive review rate
- repeat-domain exposure reduction
- appeal reversal rate

### False-positive spike after policy update

- ID: `ir_false_positive_spike`
- Severity: `sev3`
- Trigger: Reviewer dismissals and appeals increase after a new policy rule starts routing educational warnings to review.

First actions:
- Pause promotion of the new rule to public labels
- Sample dismissed cases and appeals
- Run protected-context eval and calibration cases
- Patch policy guidance before changing model thresholds

Mitigations:
- Protected-context suppression rule
- Reviewer training update
- False-positive eval gate
- Notice copy clarification

Success metrics:
- dismissal rate among reviewed items
- appeal reversal rate
- protected-context eval pass rate
- reviewer calibration accuracy

### OCR/QR scam reports with missing source context

- ID: `ir_ocr_qr_ambiguity`
- Severity: `sev3`
- Trigger: Users report screenshots containing QR codes and wallet-connection text, but source accounts and links are cropped.

First actions:
- Route to human review rather than automatic public labeling
- Ask reviewer to verify source/link context where available
- Track OCR ambiguity separately from confirmed wallet-drainer cases
- Create examples for multimodal hardening evals

Mitigations:
- OCR-specific review queue
- Source-context requirement for public labels
- Screenshot/QR evidence checklist
- User-facing notice that explains missing context decisions

Success metrics:
- OCR review precision
- time to source verification
- public-label downgrade rate
- appeal reversal rate for OCR cases
