# Stance-Aware Policy Overlay and Cascade Preregistration

**Status:** frozen before implementation evaluation and before any new hosted
request. This document does not authorize public-label publication or live
platform action.

**Contribution boundary:** this is a platform-routing evaluation, not a
general-purpose chat-safety result. The current primary-source comparison and
explicit non-claims are recorded in
[`CURRENT_RELEVANCE_AND_CONTRIBUTION_BOUNDARY.md`](CURRENT_RELEVANCE_AND_CONTRIBUTION_BOUNDARY.md).
In particular, this work does not borrow, reproduce, or infer validation from
MLCommons AILuminate Safety 1.2.1 scores, whose single-turn English
text-to-text hazardous-response scope is different from stance-aware
user-generated-content moderation.

## Question

Can a deterministic policy overlay reduce public-label candidacy for skeptical
third-party scam reportage while retaining direct-scam recall and keeping an
optional hosted guard-model cascade bounded to ambiguous cases?

## Design Principle

The overlay is derived from the policy distinction between a speaker promoting
an offer and a speaker describing it skeptically. It may use only three
generalizable signals:

1. a third-party reportage frame;
2. a contrastive doubt clause; and
3. the absence of an ask directed at the reader.

The six documented `skeptical_third_party_report` failures motivate the
problem but are **diagnostic only**. They are not a tuning target, are not used
to select patterns or thresholds, and cannot support the primary result.

The frozen StanceBench suite is the evaluation surface for this overlay. Its
results must not be used to revise patterns or thresholds. Any future revision
requires a dated deviation and a fresh holdout before its result is interpreted.

## Frozen Decision Rule

For a post with all three signals, `public_label_candidate` and
`high_confidence_escalation` are unavailable. If the existing model score meets
the frozen review threshold, route to `send_to_human_review`; otherwise return
`no_label`. A direct ask directed at the reader prevents this overlay from
activating, even if the post opens with skeptical language.

All other existing policy rules, model features, fitted coefficients, and score
thresholds remain unchanged. This is a policy-routing overlay, not a retrained
classifier.

## Hypotheses

**H1 (primary):** on the separately frozen 48-item StanceBench scams v0.1
suite, the overlay reduces the public-label rate for the 40 counter-speech
items relative to the currently pinned local baseline.

**H2:** on the 168-row primary held-out set, direct-scam review-or-label recall
does not fall below the current baseline's observed 60/60. This is a regression
guard, not independent evidence for H1 because the six diagnostic cases are in
that held-out set.

**H3:** every protected-context guard case and authored production-hardening
case remains passing. Any failure blocks a release claim.

**H4 (cost, descriptive):** applying a hosted guard only to the intermediate
review route costs less per 1K scored posts than running it on every post. The
calculation uses the audited 7.10% intermediate-review routing share from a
single 240-second public Jetstream snapshot restricted to scored English and
Spanish posts; it is not a platform-wide traffic or prevalence claim.

## Evaluation Plan

1. Validate the overlay's exact action behavior with unit tests that use
   synthetic, non-StanceBench strings.
2. Run the unchanged primary 168-row held-out set and report public-label and
   review-or-label metrics before/after. Publish the six diagnostic-case
   outcomes separately as error analysis only.
3. Run the independent frozen StanceBench input plus its 12 benign-unrelated
   controls through a new, separately pinned local-baseline condition. Report
   perpetration catch, counter-speech public-label rate, counter-speech review
   rate, and control public-label rate with exact counts and Wilson intervals.
4. Run the full release gate. Do not report a cascade-quality improvement until
   a separately preregistered shared-action hosted comparison completes.

## Cascade Cost Model

The current published Llama Guard list-price estimate is `$0.3415 / 1K posts`
when run on every post. The conditional routing estimate is that rate multiplied
by `0.071`, or approximately `$0.0242 / 1K posts`, before transport overhead.
This is an estimated routing cost only. It assumes the model is called exactly
once per intermediate-review item and excludes candidate-label/escalation
confirmation, retries, caching, and human-review costs.

## Deviations

Any change to signal patterns, thresholds, StanceBench inputs, adapter pin,
hosted model, price source, calibration denominator, or reporting metric must
be documented before interpretation. A null or adverse result will be
published with the same prominence as an improvement.
