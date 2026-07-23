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
            "usage": {key: sum(int(record["usage"].get(key, 0) or 0) for record in records) for key in ("prompt_tokens", "completion_tokens", "total_tokens")},
            "providerResolvedModelIds": sorted({record["providerModel"] for record in records}),
        }
    report = {
        "schemaVersion": 1,
        "scope": "Aggregate-only, authorized hosted comparison; raw outputs remain ignored locally.",
        "inputs": {"testRows": len(rows), "testSha256": sha256(ROOT / "test.csv"), "documentedSliceRows": len(slice_indices), "documentedSlicePath": "model_comparison/documented_skeptical_reportage_slice.json"},
        "method": {"bootstrapResamples": RESAMPLES, "bootstrapSeed": SEED, "hostedActionMapping": "SAFE -> no_action; UNSAFE -> human_review; incompatible -> excluded from action metrics. No hosted output can create a public-label candidate."},
        "cost": {"status": "not_reported", "reason": "Provider usage was cached, but no immutable provider price snapshot was captured."},
        "systems": systems,
        "interpretation": [
            "The six-case skeptical-reportage slice was documented before this hosted run. It is a targeted error-analysis slice, not a complete protected-context taxonomy.",
            "H1's public-label comparison is not estimable because the hosted mapping intentionally has no public-label action. The six-case hosted review rates are descriptive, non-primary evidence only.",
            "Llama Guard reaches 60/60 review-or-label recall with three legitimate review routes. gpt-oss reaches 59/60 with three legitimate review routes. These are offline policy-conditioned observations, not production performance claims.",
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
        "| System | Review-or-label recall | Review precision | Legitimate review routes | Documented skeptical-reportage review rate | Mean latency |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for name, system in systems.items():
        values = system["metrics"]
        slice_rate = system["documentedSkepticalReportage"]["reviewRate"]
        latency = system.get("meanLatencyMs")
        table.append(f"| {name} | {values['reviewOrLabelRecall']:.1%} | {values['reviewPrecision']:.1%} | {values['fp']} | {slice_rate:.1%} | {f'{latency:.0f} ms' if latency else 'local'} |")
    table += [
        "",
        "## Reading the result",
        "",
        "The local baseline routes all six previously documented skeptical-reportage false positives to review and scores all six as public-label candidates. Llama Guard clears all six; gpt-oss routes one of six to review. Hosted systems never produce public-label candidates under the frozen mapping, so their public-label rate is intentionally not compared as a generic classifier output.",
        "",
        "The result is useful, not conclusive: the error slice has six cases, dollar cost is intentionally omitted because no immutable provider price snapshot was captured, and this offline text-only run is not evidence of production safety. See `model_comparison/EXTERNAL_RUN_PROVENANCE.md` for routing, retries, hashes, and limits.",
    ]
    markdown_path.write_text("\n".join(table) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
