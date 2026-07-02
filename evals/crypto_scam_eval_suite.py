from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.metrics import f1_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from policy_proposal_labeler_v2 import (  # noqa: E402
    contextual_safety_evidence,
    decision_for_text,
    policy_evidence,
    public_label_evidence,
    register_pickle_compatibility,
)


ACTION_RANK = {
    "no_label": 0,
    "send_to_human_review": 1,
    "apply_potential_crypto_fraud_label": 2,
    "high_confidence_escalation": 3,
}
PUBLIC_LABEL_ACTIONS = {"apply_potential_crypto_fraud_label", "high_confidence_escalation"}


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("Eval cases file must contain a JSON list.")
    required = {"id", "scenario", "ground_truth", "expected_public_label", "text"}
    for case in cases:
        missing = sorted(required - set(case))
        if missing:
            raise ValueError(f"Case {case.get('id', '<unknown>')} missing fields: {missing}")
    return cases


def mutate_text(text: str, mutation: str) -> str:
    replacements = {
        "spaced_keywords": {
            "wallet": "w a l l e t",
            "Wallet": "W a l l e t",
            "bitcoin": "b i t c o i n",
            "Bitcoin": "B i t c o i n",
            "airdrop": "a i r d r o p",
            "claim": "c l a i m",
            "connect": "c o n n e c t",
            "crypto": "c r y p t o",
        },
        "leetspeak": {
            "official": "0fficial",
            "wallet": "w4llet",
            "bitcoin": "b1tc0in",
            "crypto": "crypt0",
            "free": "fr33",
            "claim": "cl4im",
            "connect": "c0nnect",
            "guaranteed": "guar4nteed",
        },
        "punctuation_noise": {
            "claim": "c.l.a.i.m",
            "wallet": "wall-et",
            "airdrop": "air drop",
            "send": "s e n d",
            "limited": "lim-ited",
        },
    }
    mutated = text
    for source, target in replacements[mutation].items():
        mutated = mutated.replace(source, target)
    if mutation == "punctuation_noise":
        mutated = mutated + " Visit hxxps://secure-airdrop dot xyz for details."
    return mutated


def adversarial_cases(cases: list[dict[str, Any]], *, max_seed_cases: int = 7) -> list[dict[str, Any]]:
    generated: list[dict[str, Any]] = []
    seed_cases = [
        case
        for case in cases
        if case.get("adversarial_seed") and case.get("ground_truth") == "fraud"
    ][:max_seed_cases]
    for case in seed_cases:
        for mutation in ("spaced_keywords", "leetspeak", "punctuation_noise"):
            generated.append(
                {
                    **case,
                    "id": f"{case['id']}__{mutation}",
                    "scenario": f"adversarial_{case['scenario']}",
                    "text": mutate_text(case["text"], mutation),
                    "tags": sorted(set(case.get("tags", []) + ["adversarial", mutation])),
                    "generated_from": case["id"],
                    "mutation": mutation,
                    "rationale": f"Adversarial mutation of {case['id']} using {mutation}.",
                }
            )
    return generated


def load_artifact(model_path: Path) -> tuple[object, dict[str, float]]:
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model artifact: {model_path}")
    register_pickle_compatibility()
    artifact = joblib.load(model_path)
    thresholds = artifact.get(
        "thresholds",
        {
            "review": artifact["threshold"],
            "label": artifact["threshold"],
            "high_confidence": artifact["threshold"],
        },
    )
    return artifact["model"], thresholds


def score_case(case: dict[str, Any], model: object, thresholds: dict[str, float]) -> dict[str, Any]:
    text = case["text"]
    probability = float(model.predict_proba([text])[0, 1])
    action = decision_for_text(text, probability, thresholds)
    public_label = action in PUBLIC_LABEL_ACTIONS
    review_or_label = action != "no_label"
    evidence = policy_evidence(text)
    public_evidence = public_label_evidence(text)
    context_evidence = contextual_safety_evidence(text)
    expected_min = case.get("expected_min_action")
    expected_max = case.get("expected_max_action")

    failures = []
    if public_label != bool(case["expected_public_label"]):
        failures.append("public_label_expectation")
    if "expected_review_or_label" in case and review_or_label != bool(case["expected_review_or_label"]):
        failures.append("review_routing_expectation")
    if expected_min and ACTION_RANK[action] < ACTION_RANK[expected_min]:
        failures.append("below_min_action")
    if expected_max and ACTION_RANK[action] > ACTION_RANK[expected_max]:
        failures.append("above_max_action")

    return {
        **case,
        "probability": probability,
        "action": action,
        "public_label": public_label,
        "review_or_label": review_or_label,
        "policy_score": evidence["score"],
        "matched_rules": public_evidence["matched_rules"],
        "public_label_rules": public_evidence["public_label_rules"],
        "contextual_safety_evidence": context_evidence,
        "passed_expectations": not failures,
        "failures": failures,
    }


def binary_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    labeled = [item for item in results if item["ground_truth"] in {"fraud", "legitimate"}]
    y_true = np.asarray([1 if item["ground_truth"] == "fraud" else 0 for item in labeled], dtype=int)
    y_public = np.asarray([1 if item["public_label"] else 0 for item in labeled], dtype=int)
    y_review = np.asarray([1 if item["review_or_label"] else 0 for item in labeled], dtype=int)
    y_threshold = np.asarray(
        [1 if item["probability"] >= item["thresholds"]["label"] else 0 for item in labeled],
        dtype=int,
    )

    return {
        "evaluated_cases": len(labeled),
        "public_label": metric_block(y_true, y_public),
        "review_or_label": metric_block(y_true, y_review),
        "pure_threshold": metric_block(y_true, y_threshold),
    }


def metric_block(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float | int]:
    tp = int(((y_true == 1) & (y_pred == 1)).sum())
    tn = int(((y_true == 0) & (y_pred == 0)).sum())
    fp = int(((y_true == 0) & (y_pred == 1)).sum())
    fn = int(((y_true == 1) & (y_pred == 0)).sum())
    return {
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tp": tp,
    }


def grouped_summary(results: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        grouped[str(item.get(field, "unknown"))].append(item)
    summary = {}
    for key, items in sorted(grouped.items()):
        summary[key] = {
            "count": len(items),
            "passed": sum(1 for item in items if item["passed_expectations"]),
            "pass_rate": sum(1 for item in items if item["passed_expectations"]) / max(1, len(items)),
            "public_labels": sum(1 for item in items if item["public_label"]),
            "review_or_label": sum(1 for item in items if item["review_or_label"]),
            "avg_probability": sum(item["probability"] for item in items) / max(1, len(items)),
        }
    return summary


def standards_summary(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        for standard in item.get("standards", []):
            grouped[standard].append(item)
    return {
        standard: {
            "count": len(items),
            "passed": sum(1 for item in items if item["passed_expectations"]),
            "pass_rate": sum(1 for item in items if item["passed_expectations"]) / max(1, len(items)),
        }
        for standard, items in sorted(grouped.items())
    }


def top_failures(results: list[dict[str, Any]], *, limit: int = 8) -> list[dict[str, Any]]:
    failures = [item for item in results if not item["passed_expectations"]]
    failures.sort(key=lambda item: (len(item["failures"]), item["probability"]), reverse=True)
    return [
        {
            "id": item["id"],
            "scenario": item["scenario"],
            "ground_truth": item["ground_truth"],
            "probability": item["probability"],
            "action": item["action"],
            "failures": item["failures"],
            "text": item["text"],
            "rationale": item.get("rationale", ""),
        }
        for item in failures[:limit]
    ]


def compact_lab_summary(report: dict[str, Any]) -> dict[str, Any]:
    public_label = report["binary_metrics"]["public_label"]
    review_or_label = report["binary_metrics"]["review_or_label"]
    robustness = report["adversarial_robustness"]
    return {
        "generatedAt": report["generated_at"],
        "caseCount": report["case_count"],
        "baseCaseCount": report["base_case_count"],
        "adversarialCaseCount": report["adversarial_case_count"],
        "expectationPassRate": report["expectation_pass_rate"],
        "publicLabelPrecision": public_label["precision"],
        "publicLabelRecall": public_label["recall"],
        "publicLabelF1": public_label["f1"],
        "reviewOrLabelRecall": review_or_label["recall"],
        "adversarialPassRate": robustness["pass_rate"],
        "adversarialPublicLabelRecall": robustness["public_label_recall"],
        "actionCounts": report["action_counts"],
        "topFailureIds": [item["id"] for item in report["top_failures"]],
    }


def write_lab_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(summary, indent=2)
    path.write_text(f"export const evalSummary = {rendered};\n", encoding="utf-8")


def build_report(
    base_cases: list[dict[str, Any]],
    results: list[dict[str, Any]],
    thresholds: dict[str, float],
) -> dict[str, Any]:
    generated = [item for item in results if "generated_from" in item]
    adversarial_passed = sum(1 for item in generated if item["passed_expectations"])
    adversarial_public_labels = sum(1 for item in generated if item["public_label"])
    action_counts = Counter(item["action"] for item in results)
    failure_counts = Counter(failure for item in results for failure in item["failures"])

    report = {
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "suite": "crypto_scam_policy_eval_v1",
        "caveat": (
            "This is an authored scenario and adversarial eval suite, not an untouched benchmark. "
            "It is designed to make policy boundaries, review-routing expectations, and false-positive risks inspectable."
        ),
        "thresholds": thresholds,
        "case_count": len(results),
        "base_case_count": len(base_cases),
        "adversarial_case_count": len(generated),
        "expectation_passed": sum(1 for item in results if item["passed_expectations"]),
        "expectation_pass_rate": sum(1 for item in results if item["passed_expectations"]) / max(1, len(results)),
        "binary_metrics": binary_metrics([{**item, "thresholds": thresholds} for item in results]),
        "action_counts": dict(sorted(action_counts.items())),
        "failure_counts": dict(sorted(failure_counts.items())),
        "context_guardrail_counts": {
            "public_label_suppressed": sum(
                1
                for item in results
                if item["contextual_safety_evidence"]["public_label_suppressed"]
            ),
            "review_preferred": sum(
                1
                for item in results
                if item["contextual_safety_evidence"]["review_preferred"]
            ),
        },
        "scenario_summary": grouped_summary(results, "scenario"),
        "ground_truth_summary": grouped_summary(results, "ground_truth"),
        "standards_summary": standards_summary(results),
        "adversarial_robustness": {
            "count": len(generated),
            "passed": adversarial_passed,
            "pass_rate": adversarial_passed / max(1, len(generated)),
            "public_label_recall": adversarial_public_labels / max(1, len(generated)),
        },
        "top_failures": top_failures(results),
        "results": results,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Scenario and adversarial eval suite for the crypto scam labeler.")
    parser.add_argument("--cases", default=str(ROOT / "evals" / "scenario_eval_cases.json"))
    parser.add_argument("--model-path", default=str(ROOT / "audit_outputs" / "fraud_labeler_v2.joblib"))
    parser.add_argument("--out", default=str(ROOT / "audit_outputs" / "eval_suite_report.json"))
    parser.add_argument("--lab-summary", default=str(ROOT / "crypto-scam-lab" / "data" / "evalSummary.js"))
    parser.add_argument("--no-adversarial", action="store_true")
    args = parser.parse_args()

    base_cases = load_cases(Path(args.cases))
    all_cases = list(base_cases)
    if not args.no_adversarial:
        all_cases.extend(adversarial_cases(base_cases))

    model, thresholds = load_artifact(Path(args.model_path))
    results = [score_case(case, model, thresholds) for case in all_cases]
    report = build_report(base_cases, results, thresholds)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_lab_summary(Path(args.lab_summary), compact_lab_summary(report))
    print(json.dumps(compact_lab_summary(report), indent=2))


if __name__ == "__main__":
    main()
