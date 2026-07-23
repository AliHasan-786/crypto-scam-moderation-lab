# OpenRouter List-Price Snapshot (2026-07-23)

This is a dated reconstruction for the completed v1 run, not an invoice or a
claim of exact charged cost. The retained cache contains final-response token
usage. It does not retain the billable usage for the three original blank
gpt-oss responses that were retried, so the estimate is a lower bound for the
complete execution.

| Model | Input list price | Output list price | Source retrieved 2026-07-23 |
| --- | ---: | ---: | --- |
| `meta-llama/llama-guard-4-12b` | $0.18 / 1M | $0.18 / 1M | [OpenRouter pricing](https://openrouter.ai/meta-llama/llama-guard-4-12b/pricing) |
| `openai/gpt-oss-safeguard-20b` | $0.075 / 1M | $0.30 / 1M | [OpenRouter pricing](https://openrouter.ai/openai/gpt-oss-safeguard-20b/pricing) |

The report calculates `input_tokens * input_rate + output_tokens * output_rate`
from these list rates. It does not assume prompt-cache discounts or include
provider fees, taxes, or retry usage unavailable in the final cache.
