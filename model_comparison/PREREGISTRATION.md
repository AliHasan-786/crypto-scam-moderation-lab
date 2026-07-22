# Guard-Model Benchmark Preregistration

**Status:** frozen before any external request. **No external model has run.**

## 1. Question

Do generic safety systems over-flag skeptical reportage and other protected
crypto-scam contexts relative to the lab's three-action policy boundary?

## 2. Frozen Inputs

- Primary dataset: hash-pinned `test.csv` (168 rows) in `evals/MANIFEST.json`.
- Protected-context analysis: every held-out legitimate item tagged as warning,
  skeptical report, news/reportage, satire, research, debugging, or help-seeking.
- Preprocessing: original post text only; no translation, retrieval, account
  metadata, URL fetch, or added context.
- Lab action vocabulary: `public_label_candidate`, `human_review`, `no_action`.

## 3. Numbered Hypotheses

**H1 (headline):** at least one compatible generic guard model has a higher
skeptical-reportage public-label-candidate rate than the local baseline. The
baseline reference is its protected-context `public_label_candidate` rate on
the frozen slice; no threshold changes are permitted after results are seen.

**H2:** compatible guard models reduce review-or-label recall on direct scam
posts or produce no compatible action mapping. Both outcomes are reported, not
treated as model failures to be hidden.

**H3:** no model dominates simultaneously on protected-context false positives,
public-label precision, review-or-label recall, latency, and estimated cost.

## 4. Primary Metric and Uncertainty

The primary metric is protected-context public-label-candidate rate:

`count(public_label_candidate among protected-context legitimate items) / N`

For each compatible system, report numerator, denominator, and a two-sided 95%
percentile bootstrap confidence interval using 10,000 fixed-seed resamples.
Report the paired difference from baseline with the same procedure. Small-N
intervals are interpreted as uncertainty, not as proof of no difference.

Secondary metrics: public-label precision, review-or-label recall, action
distribution, per-false-positive-class rates, latency, and estimated cost per
1K posts. Incompatible mappings are listed separately and excluded from numeric
comparisons.

## 5. Pinned Systems and Output-to-Action Mapping

| System | Pinned identifier / access | Native output to lab action |
| --- | --- | --- |
| Lab baseline | local TF-IDF artifact | native thresholds |
| OpenAI Moderation | `omni-moderation-latest` via OpenAI | only a policy-compatible scam/fraud positive may map to review; generic category positives without a compatible rationale are incompatible, never public-label candidates |
| Llama Guard 4 | `meta-llama/llama-guard-4-12b` via Groq | policy-prompted `safe` -> no action; scam-policy violation with direct speaker-originated evidence -> review; all uncertain/protected contexts -> review |
| ShieldGemma text | `google/shieldgemma-2b` local | policy-prompted unsafe output maps to review only; no public-label mapping without direct-evidence schema |
| gpt-oss safeguard | `gpt-oss-safeguard-20b` via Groq | policy-prompted scam violation with direct speaker-originated evidence -> review; all other unsafe/inconclusive outputs -> review |

No external system receives a public-label-candidate mapping unless its output
contains the frozen direct-evidence fields. “No compatible mapping” is a valid
published result.

## 6. Run Order and Deviations

Validate hashes; record `.env` key presence without exposing values; run local
baseline; then OpenAI, Llama Guard, ShieldGemma, and gpt-oss in that order.
Cache raw outputs privately with model ID, provider date, prompt hash, latency,
and cost before aggregate reporting. Rerun only for documented transport or
provider failure.

Any changed model ID, prompt, mapping, input exclusion, budget exception,
rerun, or unavailable provider must be added to a dated deviation table before
interpretation. Existing results are never overwritten to improve a comparison.
