# Stance-Aware Policy Overlay Evaluation

This is a deterministic policy-routing overlay, not a retrained model. The six known skeptical-reportage failures are diagnostic only; the separately frozen StanceBench suite is the primary evaluation surface.

| Surface | System | Perpetration action-queue rate | Counter-speech public-label rate | Counter-speech review rate | Control public-label rate |
| --- | --- | ---: | ---: | ---: | ---: |
| Frozen StanceBench | legacyThresholdPolicy | 75.0% (6/8) | 52.5% (21/40; 95% Wilson 37.5%-67.1%) | 30.0% (12/40) | 0.0% (0/12) |
| Frozen StanceBench | stanceAwareOverlay | 75.0% (6/8) | 7.5% (3/40; 95% Wilson 2.6%-19.9%) | 72.5% (29/40) | 0.0% (0/12) |

## Primary Held-Out Regression Guard

Direct-scam review-or-label recall: 60/60 before, 60/60 after.
Legitimate public-label candidates: 8/108 before, 1/108 after.

## Diagnostic Cases

The six known skeptical-reportage cases are reported for transparency but are not independent validation. They were captured from the pre-overlay error analysis and frozen in `evals/diagnostic_skeptical_reportage_cases.json`:
- test-fp-045: high_confidence_escalation -> send_to_human_review
- test-fp-132: apply_potential_crypto_fraud_label -> send_to_human_review
- test-fp-135: high_confidence_escalation -> send_to_human_review
- test-fp-136: high_confidence_escalation -> send_to_human_review
- test-fp-144: high_confidence_escalation -> send_to_human_review
- test-fp-146: high_confidence_escalation -> send_to_human_review

## Bounded Cascade Cost

At the audited 7.10% intermediate-review routing share, a $0.3415 / 1K full-traffic Llama estimate becomes $0.0242 / 1K posts for conditional calls (14.1x lower model-call cost). This is a routing-cost estimate only, not an accuracy or staffing claim.
