# Hosted Guard-Model Run Provenance

## Scope

On 2026-07-23, the project owner authorized two hosted, text-only guard-model
runs over the 168-row, hash-pinned `test.csv`. Raw provider responses remain in
the ignored local cache; this repository publishes aggregate results only.

## Provider Routing

Both pinned identifiers ran through OpenRouter:

- `meta-llama/llama-guard-4-12b`
- `openai/gpt-oss-safeguard-20b`

Groq's free tier accepted one `gpt-oss` smoke request on 2026-07-22. Its Llama
Guard route had been decommissioned. That provider fact prompted a route change,
not a model substitution; the identifier is preserved in the preregistration
deviation record.

## Execution Lineage

- Initial OpenRouter smoke: one case per model; excluded from aggregate claims.
- Main run: 168 cases per model, completed in resumable batches under
  preregistration SHA-256 `6b7ee3275cb49d7a557daed5e0c7f20d566d94ff0cc6bf99f3017f112ecbcba1`.
- Three gpt-oss outputs were empty despite HTTP success. Per the preregistration
  deviation protocol, those three and only those three were rerun at a 2,400
  token budget, with the same model, inputs, system prompt, and mapping. The
  amended preregistration SHA-256 is
  `0e689f6661d68a5ae49314a227209de3b8eae2eba442e31edf0a784d78c29ee6`.

The local cache stores case index, input hash, response, provider-resolved
model, request parameters, usage, latency, timestamp, and retry attempt. It is
intentionally ignored because raw third-party responses and operational details
do not belong in the public repository.

## Limits

This is a controlled offline comparison, not a production safety claim. The
headline stance slice is the six skeptical-reportage cases pre-documented in
the error analysis; it is not a newly labeled complete taxonomy of all
legitimate test items. OpenRouter usage was retained; a provider price snapshot
was not, so the public report does not claim dollar cost or cost-per-1K.
