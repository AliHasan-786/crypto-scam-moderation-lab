# Guard-Model Comparison Preregistration

**Status:** Committed before external calls. Current execution is cache-only;
systems without an approved access path are reported as unavailable, not scored.

## Question

On identical inputs, do candidate safety systems preserve the lab's protected
contexts, especially skeptical third-party reporting, while producing an action
mapping compatible with the crypto-investment-scam policy?

## Frozen inputs and mappings

- Held-out set: `test.csv`, as hash-pinned in `evals/MANIFEST.json`.
- Input preprocessing: original post text only; no added context or translation.
- Lab actions: `public_label_candidate`, `human_review`, `no_action`.
- Native model output is mapped only when it provides enough policy-relevant
  information. An incompatible mapping is a result, not a failure to report.
- Protected-context hypothesis: generic safety systems may flag skeptical
  reporting because it repeats harmful language. We will publish this class
  breakdown and every compatible system's losses.

## Reporting commitments

Every row records model identifier, access date, provider-reported version when
available, prompt hash, preprocessing, action mapping, latency, and cost. Raw
provider output is kept only in a private cache when the access plan permits it;
the public report contains aggregate outcomes and provenance. No threshold is
tuned after observing a comparator result.
