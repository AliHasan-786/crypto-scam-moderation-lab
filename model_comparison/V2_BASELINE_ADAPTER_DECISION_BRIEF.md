# V2 Baseline Adapter Decision Brief

## Decision Needed Before a Hosted V2 Run

The preregistration says both that the shared public-label rule is applied
identically after output validation and that the local baseline begins from
its frozen score thresholds. Those statements leave one implementation choice:
whether a threshold-derived `public_label_candidate` also receives the shared
evidence and protected-context guard.

## Offline Implementation

The offline adapter applies the same guard to all systems **after** mapping the
baseline score to the three shared actions:

1. score at or above the frozen label threshold starts as
   `public_label_candidate`;
2. score at or above the frozen review threshold otherwise starts as
   `human_review`;
3. the shared contract then downgrades a public-label candidate when it lacks
   two risk indicators, speaker-originated evidence, or has protected context.

This keeps the threshold mapping frozen while ensuring that a hosted response
and a local score are evaluated against the same publication rule.

## Common Adapter Semantics

For every system, `public_label_candidate` is only provisional until the common
adapter verifies two **distinct** canonical policy risk indicators, at least one
speaker-originated evidence item, and no protected context. Unknown risk or
protected-context categories, malformed action types, missing fields, and
unsupported actions are `incompatible`; they are never converted to
`no_action`. The offline tests freeze these semantics before any transport is
introduced.

## Why It Requires Review

Without the post-mapping guard, the baseline has a privileged route unavailable
to hosted systems, so V2 would still not be a comparable three-action result.
With it, V2 measures the complete policy contract rather than raw model score.
The offline preflight is not a V2 result and makes no comparative claim.

## Recommendation

Approve the post-mapping shared guard before any V2 call. If a different
interpretation is selected, update the frozen preregistration as a dated
deviation and rerun the offline fixture tests before requesting provider access.
