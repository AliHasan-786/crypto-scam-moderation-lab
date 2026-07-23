# Hosted Guard-Model Benchmark

An authorized, aggregate-only comparison over the hash-pinned 168-row held-out set. Raw provider responses stay in an ignored local cache.

## Headline Finding

**I predicted the industry models would share my system's skeptical-reportage weakness. They did not.** On the six pre-documented cases, the baseline escalated 6/6 (all crossed its public-label threshold), Llama Guard routed 0/6 to human review, and gpt-oss routed 1/6 to human review. This directional result does not support the preregistered prediction (`n=6`).

The hosted systems had a two-action mapping while the local baseline used three actions. The table reports observed routes, not a like-for-like quality ranking; in particular, it intentionally omits review precision.

| System | Current action surface | Direct-scam recall under current mapping | Legitimate posts entering action queue | Skeptical-reportage escalation (`n=6`) | Mean latency | Est. list USD / 1K posts |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| lab-baseline | three actions | 100.0% | 27/108 | 100.0% | local | n/a |
| meta-llama/llama-guard-4-12b | two actions; not like-for-like | 100.0% | 3/108 | 0.0% | 557 ms | $0.3415 |
| openai/gpt-oss-safeguard-20b | two actions; not like-for-like | 98.3% | 3/108 | 16.7% | 1656 ms | $0.2101 |

## Reading the result

Llama Guard reached 60/60 direct-scam recall. gpt-oss reached 59/60: it cleared one direct scam that the baseline caught. Llama Guard's observed mean latency was 557 ms versus gpt-oss at 1,656 ms. Those differences, and the stance result, are reportable dimensions; none establishes production superiority.

The list-price column is reconstructed from retained final-response tokens and OpenRouter rates retrieved on 2026-07-23; it excludes unretained usage from the three blank gpt-oss attempts and is not an invoice. See `model_comparison/OPENROUTER_PRICE_SNAPSHOT_2026-07-23.md`, `model_comparison/PREREGISTRATION_V2_SHARED_ACTIONS.md`, and `model_comparison/EXTERNAL_RUN_PROVENANCE.md` for costs, the planned shared mapping, routing, retries, hashes, and limits.
