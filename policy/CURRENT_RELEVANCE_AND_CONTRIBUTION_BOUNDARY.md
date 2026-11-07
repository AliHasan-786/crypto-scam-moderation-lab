# Current Relevance and Contribution Boundary

**Recorded:** 2026-11-07  
**Scope:** `crypto-local-policy-generalization-1`  
**Status:** local policy-routing research only; not a hosted-model benchmark,
production deployment, or claim of general safety capability.

## Why This Work Is Timely

MLCommons published AILuminate Safety 1.2.1 official results on October 29,
2026. Its current Safety benchmark assesses general-purpose chat systems on
single-turn, English-language, text-to-text requests across twelve hazard
categories. It measures whether a model response is hazardous; it does not
measure a platform's decision to label user-generated content, source/speaker
intent, counter-speech protection, or the downstream cost of human review.

That boundary is useful rather than a reason to borrow an unrelated score. A
moderation system can correctly identify scam vocabulary while still making a
harmful platform decision by publicly labeling the person who is warning about
the scam. This lab studies that distinct decision boundary.

Primary sources consulted:

- [MLCommons AILuminate Safety 1.2.1 results](https://mlcommons.org/ailuminate/safety/results/)
  (retrieved 2026-11-07): scope is single-turn, English (US), text-to-text;
  scores are not certifications.
- [MLCommons Safety benchmark documentation](https://mlcommons.org/ailuminate/safety/)
  (retrieved 2026-11-07): Safety does not test long conversations, images, or
  agents, and does not measure capability, accuracy, or helpfulness.
- [MLCommons Safety methodology](https://mlcommons.org/ailuminate/safety-methodology/)
  (retrieved 2026-11-07): documents the system-under-test, evaluation, and
  benchmark-scope limitations.

No AILuminate score, model ranking, prompt, evaluator, or implied validation
is used in this repository's results.

## Specific Contribution

The contribution is a preregistered, policy-conditioned routing overlay for a
crypto-scam moderation workflow. It operationalizes three observable signals:

1. a third-party reportage frame;
2. a contrastive doubt clause; and
3. the absence of a speaker-originated ask directed at the reader.

When all three are present, the system prevents public-label candidacy and
routes remaining risk to human review. This is deliberately narrower than
claiming that a lexical classifier understands intent or that the system solves
counter-speech moderation generally.

The evaluation reports the full tradeoff rather than only an aggregate score:

- direct-scam review-or-label recall on the unchanged 168-row held-out set;
- counter-speech public-label and review rates on the separately frozen
  StanceBench suite, with exact counts and Wilson intervals;
- benign-control public-label rate;
- diagnostic outcomes for known development failures, presented separately;
- a bounded routing-cost estimate using the documented 7.10% intermediate
  review share, explicitly excluding quality, staffing, and platform-scale
  claims.

## Frozen Boundaries

- The six documented skeptical-reportage failures are development diagnostics,
  not independent confirmation of the overlay.
- The frozen StanceBench inputs are an evaluation surface, not a source of
  future pattern or threshold changes. A proposed change needs a dated
  preregistration deviation and a fresh holdout before interpretation.
- Existing model coefficients and score thresholds are unchanged. The overlay
  is policy routing, not a claim of a newly trained model.
- Local results do not establish hosted-model quality. A hosted V2 comparison
  requires the separately frozen shared-action protocol, current access and
  budget approval, and its live-transport safety gates.
- This project does not publish labels, ingest live content in the public demo,
  or use unlicensed/private user data.

## Decision Standard

The overlay is useful only if it reduces inappropriate public-label candidacy
without reducing direct-scam routing and without regressing protected-context
guards. A lower false-positive rate purchased by silently dropping scam recall
is a failure, not an improvement.
