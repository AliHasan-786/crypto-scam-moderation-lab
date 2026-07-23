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

The completed local cache stores case index, input hash, response,
provider-resolved model, request parameters, usage, latency, timestamp, and
retry attempt. The exact static prompt used for both models has SHA-256
`994837f3d384b4cc4634b7395c5f24e0030f13caf99132c92e21e790f3c2029d`,
reconstructed from the checked-in runner and policy. The original cache did not
write that value per record; future runs do. It is intentionally ignored because
raw third-party responses and operational details do not belong in the public
repository.

## Limits

This is a controlled offline comparison, not a production safety claim. The
headline stance slice is the six skeptical-reportage cases pre-documented in
the error analysis; it is not a newly labeled complete taxonomy of all
legitimate test items. The report now includes a dated, reconstructed list-price
estimate from retained final-response usage; it is not an invoice and excludes
unretained usage from the three blank gpt-oss attempts. See
`model_comparison/OPENROUTER_PRICE_SNAPSHOT_2026-07-23.md`.
