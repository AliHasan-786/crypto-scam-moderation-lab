"""Publish aggregate-only metrics from the ignored OpenRouter guard-model cache."""
from __future__ import annotations

import csv
import hashlib
import json
import random
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SEED = 20260723
RESAMPLES = 10_000
LIST_PRICES = {
    "meta-llama/llama-guard-4-12b": {"input": 0.18, "output": 0.18},
    "openai/gpt-oss-safeguard-20b": {"input": 0.075, "output": 0.30},
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interval(values: list[int]) -> list[float]:
    if not values:
        return [0.0, 0.0]
    rng = random.Random(SEED)
    samples = sorted(sum(values[rng.randrange(len(values))] for _ in values) / len(values) for _ in range(RESAMPLES))
    return [round(samples[int(RESAMPLES * 0.025)], 4), round(samples[int(RESAMPLES * 0.975) - 1], 4)]


def metrics(predictions: list[bool], labels: list[int]) -> dict[str, object]:
    tp = sum(prediction and label for prediction, label in zip(predictions, labels))
    fp = sum(prediction and not label for prediction, label in zip(predictions, labels))
    fn = sum(not prediction and label for prediction, label in zip(predictions, labels))
    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "reviewOrLabelRecall": round(tp / (tp + fn), 4) if tp + fn else None,
        "reviewPrecision": round(tp / (tp + fp), 4) if tp + fp else None,
    }


def main() -> None:
    rows = list(csv.DictReader((ROOT / "test.csv").open(encoding="utf-8-sig")))
    labels = [int(row["Ground Truth Label"]) for row in rows]
    slice_config = json.loads((ROOT / "model_comparison/documented_skeptical_reportage_slice.json").read_text(encoding="utf-8"))
    slice_indices = [case["caseIndex"] for case in slice_config["cases"]]
    for case in slice_config["cases"]:
        actual = hashlib.sha256(rows[case["caseIndex"]]["Post Content"].encode("utf-8")).hexdigest()
        if actual != case["textSha256"]:
            raise ValueError(f"slice hash mismatch for {case['caseId']}")

    artifact = joblib.load(ROOT / "audit_outputs/fraud_labeler_v2.joblib")
    scores = artifact["model"].predict_proba([row["Post Content"] for row in rows])[:, 1]
    baseline_review = [float(score) >= float(artifact["thresholds"]["review"]) for score in scores]
    baseline_label = [float(score) >= float(artifact["thresholds"]["label"]) for score in scores]
    systems = {
        "lab-baseline": {
            "modelId": "crypto-lab-tfidf-baseline",
            "route": "local",
            "metrics": metrics(baseline_review, labels),
            "documentedSkepticalReportage": {
                "reviewRate": round(sum(baseline_review[index] for index in slice_indices) / len(slice_indices), 4),
                "reviewRate95Ci": interval([int(baseline_review[index]) for index in slice_indices]),
                "publicLabelCandidateRate": round(sum(baseline_label[index] for index in slice_indices) / len(slice_indices), 4),
                "publicLabelCandidateRate95Ci": interval([int(baseline_label[index]) for index in slice_indices]),
            },
        }
    }
    for model in ("meta-llama/llama-guard-4-12b", "openai/gpt-oss-safeguard-20b"):
        path = ROOT / "model_comparison/cache" / f"openrouter__{model.replace('/', '__')}.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        if len(records) != len(rows) or {record["caseIndex"] for record in records} != set(range(len(rows))):
            raise ValueError(f"incomplete cache for {model}")
        indexed = {record["caseIndex"]: record for record in records}
        decisions = [indexed[index]["output"]["route"] == "human_review" for index in range(len(rows))]
        slice_decisions = [decisions[index] for index in slice_indices]
        usage = {key: sum(int(record["usage"].get(key, 0) or 0) for record in records) for key in ("prompt_tokens", "completion_tokens", "total_tokens")}
        estimated_cost = (usage["prompt_tokens"] * LIST_PRICES[model]["input"] + usage["completion_tokens"] * LIST_PRICES[model]["output"]) / 1_000_000
        systems[model] = {
            "modelId": model,
            "route": "OpenRouter",
            "metrics": metrics(decisions, labels),
            "documentedSkepticalReportage": {
                "reviewRate": round(sum(slice_decisions) / len(slice_decisions), 4),
                "reviewRate95Ci": interval([int(value) for value in slice_decisions]),
                "publicLabelCandidateRate": None,
                "publicLabelCandidateRate95Ci": None,
                "note": "The preregistered hosted mapping never assigns a public-label candidate; unsafe routes go to human review.",
            },
            "actionDistribution": {route: sum(record["output"]["route"] == route for record in records) for route in ("no_action", "human_review", "incompatible")},
            "meanLatencyMs": round(sum(record["latencyMs"] for record in records) / len(records), 2),
            "usage": usage,
            "estimatedListCost": {
                "usdForRetainedFinalResponses": round(estimated_cost, 6),
                "usdPer1KPosts": round(estimated_cost / len(rows) * 1000, 4),
                "note": "List-price estimate from retained final responses." if model.startswith("meta-llama") else "Lower-bound list-price estimate: excludes billable usage from three blank gpt-oss responses that were retried.",
            },
            "providerResolvedModelIds": sorted({record["providerModel"] for record in records}),
        }
    report = {
        "schemaVersion": 1,
        "scope": "Aggregate-only, authorized hosted comparison; raw outputs remain ignored locally.",
        "inputs": {"testRows": len(rows), "testSha256": sha256(ROOT / "test.csv"), "documentedSliceRows": len(slice_indices), "documentedSlicePath": "model_comparison/documented_skeptical_reportage_slice.json"},
        "method": {"bootstrapResamples": RESAMPLES, "bootstrapSeed": SEED, "hostedActionMapping": "SAFE -> no_action; UNSAFE -> human_review; incompatible -> excluded from action metrics. No hosted output can create a public-label candidate."},
        "cost": {"status": "reconstructed_list_price_estimate", "priceSnapshot": "model_comparison/OPENROUTER_PRICE_SNAPSHOT_2026-07-23.md", "limitation": "Uses dated public list rates and retained final-response usage; it is not an invoice and excludes unknown usage from three blank responses that were retried."},
        "systems": systems,
        "interpretation": [
            "The six-case skeptical-reportage slice was documented before this hosted run. It is a targeted error-analysis slice, not a complete protected-context taxonomy.",
            "The preregistered prediction that hosted guards would over-flag the documented skeptical-reportage cases was not supported on this slice: Llama Guard routed 0/6 and gpt-oss routed 1/6 to review, versus the baseline's 6/6. The slice is directional, not conclusive (n=6).",
            "The two-action hosted mapping and three-action baseline mapping are not like-for-like. The report therefore does not treat legitimate review-route counts or review precision as a model-quality ranking. V2 pre-registers a shared three-action contract before any additional calls.",
            "Llama Guard reaches 60/60 direct-scam review-or-label recall; gpt-oss reaches 59/60 and clears one direct scam. Llama Guard's mean observed latency was about three times lower. These are offline policy-conditioned observations, not production performance claims.",
        ],
        "provenance": "model_comparison/EXTERNAL_RUN_PROVENANCE.md",
    }
    json_path = ROOT / "audit_outputs/external_guard_model_benchmark.json"
    markdown_path = ROOT / "audit_outputs/external_guard_model_benchmark.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    table = [
        "# Hosted Guard-Model Benchmark",
        "",
        "An authorized, aggregate-only comparison over the hash-pinned 168-row held-out set. Raw provider responses stay in an ignored local cache.",
        "",
        "## Headline Finding",
        "",
        "**I predicted the industry models would share my system's skeptical-reportage weakness. They did not.** On the six pre-documented cases, the baseline escalated 6/6 (all crossed its public-label threshold), Llama Guard routed 0/6 to human review, and gpt-oss routed 1/6 to human review. This directional result does not support the preregistered prediction (`n=6`).",
        "",
        "The hosted systems had a two-action mapping while the local baseline used three actions. The table reports observed routes, not a like-for-like quality ranking; in particular, it intentionally omits review precision.",
        "",
        "| System | Current action surface | Direct-scam recall under current mapping | Legitimate posts entering action queue | Skeptical-reportage escalation (`n=6`) | Mean latency | Est. list USD / 1K posts |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, system in systems.items():
        values = system["metrics"]
        slice_rate = system["documentedSkepticalReportage"]["reviewRate"]
        latency = system.get("meanLatencyMs")
        action_surface = "three actions" if name == "lab-baseline" else "two actions; not like-for-like"
        reviewed_legitimate = f"{values['fp']}/108"
        cost = system.get("estimatedListCost", {}).get("usdPer1KPosts")
        table.append(f"| {name} | {action_surface} | {values['reviewOrLabelRecall']:.1%} | {reviewed_legitimate} | {slice_rate:.1%} | {f'{latency:.0f} ms' if latency else 'local'} | {f'${cost:.4f}' if cost is not None else 'n/a'} |")
    table += [
        "",
        "## Reading the result",
        "",
        "Llama Guard reached 60/60 direct-scam recall. gpt-oss reached 59/60: it cleared one direct scam that the baseline caught. Llama Guard's observed mean latency was 557 ms versus gpt-oss at 1,656 ms. Those differences, and the stance result, are reportable dimensions; none establishes production superiority.",
        "",
        "The list-price column is reconstructed from retained final-response tokens and OpenRouter rates retrieved on 2026-07-23; it excludes unretained usage from the three blank gpt-oss attempts and is not an invoice. See `model_comparison/OPENROUTER_PRICE_SNAPSHOT_2026-07-23.md`, `model_comparison/PREREGISTRATION_V2_SHARED_ACTIONS.md`, and `model_comparison/EXTERNAL_RUN_PROVENANCE.md` for costs, the planned shared mapping, routing, retries, hashes, and limits.",
    ]
    markdown_path.write_text("\n".join(table) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
