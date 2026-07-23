# External Benchmark Run Record

**Status:** completed on 2026-07-23. The two hosted guard-model runs used the
ignored local `OPENROUTER_API_KEY`. The runner persisted each response before
requesting the next one, which kept the full run resumable without repeated
calls. Published aggregate results are in
`audit_outputs/external_guard_model_benchmark.md`.

**Pinned OpenRouter routes:** `meta-llama/llama-guard-4-12b` and
`openai/gpt-oss-safeguard-20b`. Groq remains documented as an initial route:
its free account accepted a `gpt-oss` smoke request, while it had decommissioned
the Llama Guard route. The provider deviation is recorded in the
preregistration; no model was silently substituted.

The run records the preregistration hash, model identifier, provider-resolved
identifier, prompt hash, input hash, raw response, usage, and latency in a
local ignored cache. Public reporting uses only aggregate metrics and selected
documented error-class counts.
