"""Evaluate the stance-aware policy overlay without changing frozen inputs."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from policy_proposal_labeler_v2 import decision_for_text, register_pickle_compatibility


HUMAN_REVIEW_SHARE = 0.071
LLAMA_FULL_TRAFFIC_COST_PER_1K = 0.3415


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wilson_interval(successes: int, total: int) -> list[float] | None:
    if total == 0:
        return None
    z = 1.959963984540054
    rate = successes / total
    denominator = 1 + z**2 / total
    centre = (rate + z**2 / (2 * total)) / denominator
    margin = z * math.sqrt((rate * (1 - rate) + z**2 / (4 * total)) / total) / denominator
    return [round(max(0.0, centre - margin), 4), round(min(1.0, centre + margin), 4)]


def legacy_action(score: float, thresholds: dict[str, float]) -> str:
    if score >= float(thresholds["high_confidence"]):
        return "high_confidence_escalation"
    if score >= float(thresholds["label"]):
        return "apply_potential_crypto_fraud_label"
    if score >= float(thresholds["review"]):
        return "send_to_human_review"
    return "no_label"


def is_public_label(action: str) -> bool:
    return action in {"apply_potential_crypto_fraud_label", "high_confidence_escalation"}


def is_action_queue(action: str) -> bool:
    return action != "no_label"


def summarize_actions(rows: list[dict[str, object]]) -> dict[str, object]:
    count = len(rows)
    public = sum(is_public_label(str(row["action"])) for row in rows)
    review = sum(str(row["action"]) == "send_to_human_review" for row in rows)
    queue = sum(is_action_queue(str(row["action"])) for row in rows)
    return {
        "n": count,
        "publicLabelCount": public,
        "publicLabelRate": round(public / count, 4) if count else None,
        "publicLabelWilson95": wilson_interval(public, count),
        "reviewCount": review,
        "reviewRate": round(review / count, 4) if count else None,
        "actionQueueCount": queue,
        "actionQueueRate": round(queue / count, 4) if count else None,
    }


def decisions(texts: list[str], model: object, thresholds: dict[str, float], enhanced: bool) -> list[dict[str, object]]:
    scores = model.predict_proba(texts)[:, 1]
    return [
        {
            "text": text,
            "score": round(float(score), 6),
            "action": decision_for_text(text, float(score), thresholds) if enhanced else legacy_action(float(score), thresholds),
        }
        for text, score in zip(texts, scores)
    ]


def load_stancebench(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            records.append(json.loads(line))
    return records


def primary_metrics(labels: list[int], rows: list[dict[str, object]]) -> dict[str, object]:
    fraud_rows = [row for row, label in zip(rows, labels) if label == 1]
    legitimate_rows = [row for row, label in zip(rows, labels) if label == 0]
    caught = sum(is_action_queue(str(row["action"])) for row in fraud_rows)
    public_fp = sum(is_public_label(str(row["action"])) for row in legitimate_rows)
    return {
        "directScamReviewOrLabel": {"caught": caught, "total": len(fraud_rows), "rate": round(caught / len(fraud_rows), 4)},
        "legitimatePublicLabels": {"count": public_fp, "total": len(legitimate_rows), "rate": round(public_fp / len(legitimate_rows), 4)},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-path", default="audit_outputs/fraud_labeler_v2.joblib")
    parser.add_argument("--test", default="test.csv")
    parser.add_argument("--diagnostic-cases", default="evals/diagnostic_skeptical_reportage_cases.json")
    parser.add_argument("--stancebench-root", type=Path, required=True)
    parser.add_argument("--out", default="audit_outputs/stance_aware_cascade_report.json")
    parser.add_argument("--markdown-out", default="audit_outputs/stance_aware_cascade_report.md")
    args = parser.parse_args()

    register_pickle_compatibility()
    artifact = joblib.load(ROOT / args.model_path)
    model, thresholds = artifact["model"], artifact["thresholds"]
    test_path = ROOT / args.test
    test_rows = list(csv.DictReader(test_path.open(encoding="utf-8-sig")))
    test_texts = [row["Post Content"] for row in test_rows]
    test_labels = [int(row["Ground Truth Label"]) for row in test_rows]
    primary_legacy = decisions(test_texts, model, thresholds, enhanced=False)
    primary_enhanced = decisions(test_texts, model, thresholds, enhanced=True)

    stance_root = args.stancebench_root.resolve()
    stance_path = stance_root / "data/frozen/scams_v0_1/stance_tuples.jsonl"
    control_path = stance_root / "data/frozen/scams_v0_1_controls/stance_tuples.jsonl"
    stance_items = load_stancebench(stance_path)
    control_items = load_stancebench(control_path)
    stance_legacy = decisions([str(item["text"]) for item in stance_items], model, thresholds, enhanced=False)
    stance_enhanced = decisions([str(item["text"]) for item in stance_items], model, thresholds, enhanced=True)
    control_legacy = decisions([str(item["text"]) for item in control_items], model, thresholds, enhanced=False)
    control_enhanced = decisions([str(item["text"]) for item in control_items], model, thresholds, enhanced=True)

    counter_indices = [index for index, item in enumerate(stance_items) if item["expected_action"] == "no_flag"]
    perpetration_indices = [index for index, item in enumerate(stance_items) if item["expected_action"] == "flag"]
    diagnostic_fixture_path = ROOT / args.diagnostic_cases
    diagnostic_fixture = json.loads(diagnostic_fixture_path.read_text(encoding="utf-8"))
    diagnostic = []
    for item in diagnostic_fixture["cases"]:
        index = next(index for index, text in enumerate(test_texts) if text == item["text"])
        diagnostic.append({
            "caseId": item["caseId"],
            "caseIndex": index,
            "legacyAction": primary_legacy[index]["action"],
            "enhancedAction": primary_enhanced[index]["action"],
        })

    def subset(rows: list[dict[str, object]], indices: list[int]) -> list[dict[str, object]]:
        return [rows[index] for index in indices]

    full_cost = LLAMA_FULL_TRAFFIC_COST_PER_1K
    conditional_cost = full_cost * HUMAN_REVIEW_SHARE
    report = {
        "schemaVersion": 1,
        "status": "local_overlay_evaluation",
        "preregistration": "policy/STANCE_AWARE_CASCADE_PREREGISTRATION.md",
        "inputs": {
            "primaryTest": {"path": args.test, "sha256": sha256(test_path), "rows": len(test_rows)},
            "stancebench": {"path": str(stance_path), "sha256": sha256(stance_path), "rows": len(stance_items)},
            "controls": {"path": str(control_path), "sha256": sha256(control_path), "rows": len(control_items)},
        },
        "model": {"path": args.model_path, "sha256": sha256(ROOT / args.model_path), "thresholds": thresholds},
        "primaryHeldout": {
            "legacyThresholdPolicy": primary_metrics(test_labels, primary_legacy),
            "stanceAwareOverlay": primary_metrics(test_labels, primary_enhanced),
            "diagnosticKnownSkepticalReportage": diagnostic,
            "note": "The six diagnostic cases are inside this held-out set and are not independent validation for the overlay.",
        },
        "stancebench": {
            "legacyThresholdPolicy": {
                "perpetration": summarize_actions(subset(stance_legacy, perpetration_indices)),
                "counterSpeech": summarize_actions(subset(stance_legacy, counter_indices)),
                "controls": summarize_actions(control_legacy),
            },
            "stanceAwareOverlay": {
                "perpetration": summarize_actions(subset(stance_enhanced, perpetration_indices)),
                "counterSpeech": summarize_actions(subset(stance_enhanced, counter_indices)),
                "controls": summarize_actions(control_enhanced),
            },
            "note": "Frozen synthetic English-first evaluation; exact counts and Wilson intervals are descriptive, not production prevalence.",
        },
        "cascadeCostEstimate": {
            "humanReviewRoutingShare": HUMAN_REVIEW_SHARE,
            "scope": "7.10% intermediate send_to_human_review routing share among 8,210 scored EN/ES posts in one 240-second public Jetstream snapshot; not platform prevalence or total human-operated queue share.",
            "fullTrafficLlamaListUsdPer1KPosts": full_cost,
            "conditionalLlamaListUsdPer1KPosts": round(conditional_cost, 4),
            "relativeReduction": round(full_cost / conditional_cost, 2),
            "limitations": "Routing-cost estimate only; excludes candidate-label/escalation confirmation, retries, caching, transport overhead, human review, and any quality claim.",
        },
    }
    json_path, markdown_path = ROOT / args.out, ROOT / args.markdown_out
    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Stance-Aware Policy Overlay Evaluation",
        "",
        "This is a deterministic policy-routing overlay, not a retrained model. The six known skeptical-reportage failures are diagnostic only; the separately frozen StanceBench suite is the primary evaluation surface.",
        "",
        "| Surface | System | Perpetration action-queue rate | Counter-speech public-label rate | Counter-speech review rate | Control public-label rate |",
        "| --- | --- | ---: | ---: | ---: | ---: |",
    ]
    for name, result in report["stancebench"].items():
        if name == "note":
            continue
        lines.append(
            f"| Frozen StanceBench | {name} | {result['perpetration']['actionQueueRate']:.1%} ({result['perpetration']['actionQueueCount']}/{result['perpetration']['n']}) | {result['counterSpeech']['publicLabelRate']:.1%} ({result['counterSpeech']['publicLabelCount']}/{result['counterSpeech']['n']}; 95% Wilson {result['counterSpeech']['publicLabelWilson95'][0]:.1%}-{result['counterSpeech']['publicLabelWilson95'][1]:.1%}) | {result['counterSpeech']['reviewRate']:.1%} ({result['counterSpeech']['reviewCount']}/{result['counterSpeech']['n']}) | {result['controls']['publicLabelRate']:.1%} ({result['controls']['publicLabelCount']}/{result['controls']['n']}) |"
        )
    legacy = report["primaryHeldout"]["legacyThresholdPolicy"]
    enhanced = report["primaryHeldout"]["stanceAwareOverlay"]
    lines += [
        "",
        "## Primary Held-Out Regression Guard",
        "",
        f"Direct-scam review-or-label recall: {legacy['directScamReviewOrLabel']['caught']}/{legacy['directScamReviewOrLabel']['total']} before, {enhanced['directScamReviewOrLabel']['caught']}/{enhanced['directScamReviewOrLabel']['total']} after.",
        f"Legitimate public-label candidates: {legacy['legitimatePublicLabels']['count']}/{legacy['legitimatePublicLabels']['total']} before, {enhanced['legitimatePublicLabels']['count']}/{enhanced['legitimatePublicLabels']['total']} after.",
        "",
        "## Diagnostic Cases",
        "",
        "The six known skeptical-reportage cases are reported for transparency but are not independent validation. They were captured from the pre-overlay error analysis and frozen in `evals/diagnostic_skeptical_reportage_cases.json`:",
    ]
    lines += [f"- {item['caseId']}: {item['legacyAction']} -> {item['enhancedAction']}" for item in diagnostic]
    lines += [
        "",
        "## Bounded Cascade Cost",
        "",
        f"At the audited 7.10% intermediate-review routing share, a $0.3415 / 1K full-traffic Llama estimate becomes ${conditional_cost:.4f} / 1K posts for conditional calls ({full_cost / conditional_cost:.1f}x lower model-call cost). This is a routing-cost estimate only, not an accuracy or staffing claim.",
    ]
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
