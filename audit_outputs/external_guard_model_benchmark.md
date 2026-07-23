# Hosted Guard-Model Benchmark

An authorized, aggregate-only comparison over the hash-pinned 168-row held-out set. Raw provider responses stay in an ignored local cache.

| System | Review-or-label recall | Review precision | Legitimate review routes | Documented skeptical-reportage review rate | Mean latency |
| --- | ---: | ---: | ---: | ---: | ---: |
| lab-baseline | 100.0% | 69.0% | 27 | 100.0% | local |
| meta-llama/llama-guard-4-12b | 100.0% | 95.2% | 3 | 0.0% | 557 ms |
| openai/gpt-oss-safeguard-20b | 98.3% | 95.2% | 3 | 16.7% | 1656 ms |

## Reading the result

The local baseline routes all six previously documented skeptical-reportage false positives to review and scores all six as public-label candidates. Llama Guard clears all six; gpt-oss routes one of six to review. Hosted systems never produce public-label candidates under the frozen mapping, so their public-label rate is intentionally not compared as a generic classifier output.

The result is useful, not conclusive: the error slice has six cases, dollar cost is intentionally omitted because no immutable provider price snapshot was captured, and this offline text-only run is not evidence of production safety. See `model_comparison/EXTERNAL_RUN_PROVENANCE.md` for routing, retries, hashes, and limits.
