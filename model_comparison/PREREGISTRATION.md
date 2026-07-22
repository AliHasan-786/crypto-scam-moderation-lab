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

## Hypotheses and analysis plan

**Primary hypothesis:** on the protected skeptical-reportage slice, at least
one compatible generic safety system will have a higher false-positive action
rate than the lab baseline's `public_label_candidate` rate. The result may also
be null; that outcome is reported unchanged.

**Primary metric:** protected-context false-positive action rate, calculated as
`public_label_candidate / protected-context items` after each system's frozen
native-output-to-action mapping. The report includes a two-sided 95% percentile
bootstrap confidence interval (10,000 resamples) and the raw numerator and
denominator. Systems with no compatible mapping are excluded from the estimate
and listed in the unavailable/incompatible table.

**Secondary metrics:** overall review-or-label recall, public-label precision,
latency, estimated cost, and action-distribution distance from the local
baseline. No system is ranked by a single aggregate score.

**Run order:** validate hashes and preprocessing; run the local baseline; run
each external system once in the order fixed in `config.json`; cache raw
provider outputs privately; validate mappings; generate the report. A rerun is
allowed only for documented provider or transport failure, never to improve a
result.

**Deviations:** any changed model identifier, prompt, preprocessing, action
mapping, input exclusion, budget exception, or rerun is logged in a dated
deviation table before the affected result is interpreted. Results already
generated are not overwritten.
