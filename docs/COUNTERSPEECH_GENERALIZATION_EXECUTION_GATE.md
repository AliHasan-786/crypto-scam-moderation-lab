# Counter-Speech Generalization Execution Gate

**Assignment:** `crypto-local-policy-generalization-1`  
**Recorded:** 2026-11-07  
**Status:** no-call execution protocol. No distribution-shift corpus has been
collected, labeled, or scored under this protocol.

## Decision the Study Would Inform

The current local result shows a policy-routing tradeoff on frozen, authored
evaluation inputs. This extension asks a narrower operational question:

> On a time-separated, rights-reviewed sample, does the frozen overlay reduce
> inappropriate public-label candidacy for protected counter-speech without
> reducing scam routing or creating an unacceptable human-review load?

The decision is whether to keep the overlay as a review-first guardrail. It is
not a decision to publish labels automatically, and it cannot establish a
general safety ranking for any model.

## Current Context and Contribution Boundary

The current [MLCommons AILuminate Safety
documentation](https://mlcommons.org/ailuminate/safety/) and [Safety 1.2.1
results](https://mlcommons.org/ailuminate/safety/results/) were retrieved on
2026-11-07. They describe a benchmark for single-turn English text-to-text
hazardous model responses, not source-speaker attribution, content-labeling
policy, or review-queue economics. This extension therefore contributes a
different artifact: a reproducible protocol for measuring policy-conditioned
counter-speech routing and its tradeoffs. It does not use, borrow, or imply any
AILuminate score or validation.

See [Current Relevance and Contribution
Boundary](../policy/CURRENT_RELEVANCE_AND_CONTRIBUTION_BOUNDARY.md) for the
complete non-claims and source record.

## Frozen System and Development Separation

Before sample collection, record in a private manifest:

- the commit SHA, model artifact SHA-256, threshold values, policy-overlay
  source hash, and evaluation-script SHA-256;
- the source window, language filter, de-duplication rule, retention schedule,
  named operator, and rights/terms review;
- an explicit declaration that the six prior skeptical-reportage errors are
  development diagnostics only.

No patterns, thresholds, model coefficients, action mapping, or review rubric
may change after this record is written. The existing frozen StanceBench suite
also remains closed to iteration; it is not a pool of new development examples.

## Collection and Access Gate

All conditions below must hold before collecting any post:

1. The shadow-service gate is passed for the proposed collection mechanism,
   including a named kill-switch owner and a written rate/storage limit.
2. The source's current terms, API rules, and retention posture are reviewed;
   no raw text or identifiers are committed to this repository.
3. Collection is read-only, bounded, and excludes private/deleted/unreadable
   material, duplicates, and records outside the preregistered language scope.
4. Only metadata, content hashes, exclusion counts, and aggregate releases are
   public. Raw materials remain access-controlled for the approved retention
   period.
5. The first frozen sample remains unavailable to model/policy development for
   at least 30 days before any human labeling begins.

Failure of any condition stops the study rather than replacing the sample with
convenient authored examples.

## Evaluation Protocol

- **Minimum target:** 200 eligible records after exclusions. Report the source
  window, all exclusion counts, and final sample size.
- **Blind scoring:** generate baseline and overlay actions before human labels
  are revealed to the experimenter who computes results.
- **Labeling:** two reviewers independently apply
  [`quality/REVIEWER_CALIBRATION_GUIDE.md`](../quality/REVIEWER_CALIBRATION_GUIDE.md).
  Record agreement and adjudication categories. If only one reviewer is
  available, disclose it and do not report inter-rater agreement.
- **Primary protected-context metric:** among human-confirmed protected
  counter-speech items, public-label-candidate rate for baseline versus overlay,
  with counts and 95% confidence intervals.
- **Safety metrics:** direct-scam review-or-label recall; public-label
  precision; protected-context review rate; overall review share; and action
  distribution. Report each baseline-to-overlay difference with uncertainty.
- **Failure condition:** a decrease in direct-scam routing, an increase in
  inappropriate public-label candidacy, or a review-load increase that exceeds
  the preregistered operating threshold is an adverse result and is published.

The existing 7.10% routing-cost estimate is not an operating threshold and is
not a predicted result for this future sample.

## Required Release Artifact

The public release must include the frozen manifest, aggregate metrics,
confidence intervals, error categories, exclusions, reviewer limitations,
provenance hashes, and the result whether favorable, null, or adverse. It must
separate historical coursework, the existing synthetic/frozen evaluations, and
this later time-separated measurement.

Until that artifact exists, the only completed local evidence is the published
frozen-evaluation result in
[`audit_outputs/stance_aware_cascade_report.md`](../audit_outputs/stance_aware_cascade_report.md).
