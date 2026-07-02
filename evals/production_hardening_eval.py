from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evals"))

from bluesky_integration.url_evidence import analyze_text_urls  # noqa: E402
from crypto_scam_eval_suite import load_artifact, score_case, top_failures  # noqa: E402
from policy_proposal_labeler_v2 import canonicalize_for_policy  # noqa: E402


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("Hardening eval cases file must contain a JSON list.")
    required = {"id", "scenario", "ground_truth", "expected_public_label", "text", "dimensions"}
    for case in cases:
        missing = sorted(required - set(case))
        if missing:
            raise ValueError(f"Case {case.get('id', '<unknown>')} missing fields: {missing}")
    return cases


def augment_result(result: dict[str, Any]) -> dict[str, Any]:
    text = result["text"]
    canonicalized = canonicalize_for_policy(text)
    url_evidence = analyze_text_urls(text)
    return {
        **result,
        "canonicalization": {
            "applied": canonicalized != text,
            "canonicalizedText": canonicalized,
        },
        "urlEvidence": url_evidence,
    }


def dimension_summary(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        for dimension in item.get("dimensions", []):
            grouped[dimension].append(item)
    summary = {}
    for dimension, items in sorted(grouped.items()):
        passed = sum(1 for item in items if item["passed_expectations"])
        public_labels = sum(1 for item in items if item["public_label"])
        review_or_label = sum(1 for item in items if item["review_or_label"])
        summary[dimension] = {
            "count": len(items),
            "passed": passed,
            "passRate": passed / max(1, len(items)),
            "publicLabels": public_labels,
            "reviewOrLabel": review_or_label,
        }
    return summary


def standard_summary(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in results:
        for standard in item.get("standards", []):
            grouped[standard].append(item)
    return {
        standard: {
            "count": len(items),
            "passed": sum(1 for item in items if item["passed_expectations"]),
            "passRate": sum(1 for item in items if item["passed_expectations"]) / max(1, len(items)),
        }
        for standard, items in sorted(grouped.items())
    }


def metric_rate(items: list[dict[str, Any]], predicate) -> float:
    if not items:
        return 1.0
    return sum(1 for item in items if predicate(item)) / len(items)


def url_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    factor_counts = Counter()
    examples = []
    for item in results:
        evidence = item["urlEvidence"]
        factor_counts.update(evidence.get("factorCounts", {}))
        for url in evidence.get("urls", []):
            examples.append(
                {
                    "caseId": item["id"],
                    "domain": url["domain"],
                    "riskWeight": url["riskWeight"],
                    "riskFactors": url["riskFactors"],
                }
            )
    examples.sort(key=lambda item: item["riskWeight"], reverse=True)
    return {
        "caseCountWithUrls": sum(1 for item in results if item["urlEvidence"]["urlCount"] > 0),
        "factorCounts": dict(sorted(factor_counts.items())),
        "topUrlEvidence": examples[:8],
    }


def build_report(results: list[dict[str, Any]], thresholds: dict[str, float]) -> dict[str, Any]:
    fraud_cases = [item for item in results if item["ground_truth"] == "fraud"]
    legitimate_cases = [item for item in results if item["ground_truth"] == "legitimate"]
    ambiguous_cases = [item for item in results if item["ground_truth"] == "ambiguous"]
    expected_review_or_label = [item for item in results if item.get("expected_review_or_label")]
    failure_counts = Counter(failure for item in results for failure in item["failures"])

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "suite": "production_hardening_eval_v1",
        "caveat": (
            "This is an authored production-hardening suite. It is not an untouched benchmark; "
            "it probes known deployment risks such as canonicalization, URL evidence, OCR ambiguity, "
            "multilingual phrasing, and protected-context false positives."
        ),
        "thresholds": thresholds,
        "caseCount": len(results),
        "expectationPassed": sum(1 for item in results if item["passed_expectations"]),
        "expectationPassRate": metric_rate(results, lambda item: item["passed_expectations"]),
        "fraudPublicLabelRecall": metric_rate(fraud_cases, lambda item: item["public_label"]),
        "reviewOrLabelRecall": metric_rate(expected_review_or_label, lambda item: item["review_or_label"]),
        "legitimateNoPublicLabelRate": metric_rate(legitimate_cases, lambda item: not item["public_label"]),
        "ambiguousReviewRate": metric_rate(
            ambiguous_cases,
            lambda item: item["action"] == "send_to_human_review",
        ),
        "canonicalizationAppliedCount": sum(1 for item in results if item["canonicalization"]["applied"]),
        "actionCounts": dict(sorted(Counter(item["action"] for item in results).items())),
        "failureCounts": dict(sorted(failure_counts.items())),
        "dimensionSummary": dimension_summary(results),
        "standardSummary": standard_summary(results),
        "urlSummary": url_summary(results),
        "topFailures": top_failures(results),
        "results": results,
    }


def compact_lab_summary(report: dict[str, Any]) -> dict[str, Any]:
    dimensions = [
        {"name": name, **values}
        for name, values in report["dimensionSummary"].items()
    ]
    dimensions.sort(key=lambda item: (-item["count"], item["name"]))
    examples = []
    for item in report["results"]:
        examples.append(
            {
                "caseId": item["id"],
                "scenario": item["scenario"],
                "action": item["action"],
                "passed": item["passed_expectations"],
                "dimensions": item.get("dimensions", []),
                "topUrlDomain": (
                    item["urlEvidence"]["urls"][0]["domain"]
                    if item["urlEvidence"].get("urls")
                    else ""
                ),
                "topUrlFactors": (
                    item["urlEvidence"]["urls"][0]["riskFactors"]
                    if item["urlEvidence"].get("urls")
                    else []
                ),
            }
        )
    return {
        "generatedAt": report["generatedAt"],
        "caseCount": report["caseCount"],
        "expectationPassRate": report["expectationPassRate"],
        "fraudPublicLabelRecall": report["fraudPublicLabelRecall"],
        "reviewOrLabelRecall": report["reviewOrLabelRecall"],
        "legitimateNoPublicLabelRate": report["legitimateNoPublicLabelRate"],
        "ambiguousReviewRate": report["ambiguousReviewRate"],
        "canonicalizationAppliedCount": report["canonicalizationAppliedCount"],
        "urlCaseCount": report["urlSummary"]["caseCountWithUrls"],
        "dimensionSummary": dimensions[:8],
        "topUrlEvidence": report["urlSummary"]["topUrlEvidence"][:5],
        "topFailureIds": [item["id"] for item in report["topFailures"]],
        "examples": examples[:6],
    }


def humanize(value: str) -> str:
    return str(value).replace("_", " ").title()


def write_lab_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(summary, indent=2)
    path.write_text(f"export const hardeningSummary = {rendered};\n", encoding="utf-8")


def write_markdown(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Production Hardening Eval Report",
        "",
        report["caveat"],
        "",
        "## Summary",
        "",
        f"- Cases: {report['caseCount']}",
        f"- Expectation pass rate: {report['expectationPassRate']:.1%}",
        f"- Fraud public-label recall: {report['fraudPublicLabelRecall']:.1%}",
        f"- Review-or-label recall for expected review cases: {report['reviewOrLabelRecall']:.1%}",
        f"- Legitimate no-public-label rate: {report['legitimateNoPublicLabelRate']:.1%}",
        f"- Ambiguous review rate: {report['ambiguousReviewRate']:.1%}",
        f"- Canonicalization applied in: {report['canonicalizationAppliedCount']} cases",
        f"- Cases with URL evidence: {report['urlSummary']['caseCountWithUrls']}",
        "",
        "## Dimensions",
        "",
    ]
    for name, summary in report["dimensionSummary"].items():
        lines.append(
            f"- {humanize(name)}: {summary['passed']}/{summary['count']} passed "
            f"({summary['passRate']:.1%})"
        )

    lines.extend(["", "## URL Evidence", ""])
    for example in report["urlSummary"]["topUrlEvidence"]:
        factors = ", ".join(humanize(factor) for factor in example["riskFactors"]) or "none"
        lines.append(
            f"- {example['caseId']}: `{example['domain']}` "
            f"risk {example['riskWeight']:.2f}; {factors}"
        )

    lines.extend(["", "## Top Failures", ""])
    if report["topFailures"]:
        for failure in report["topFailures"]:
            lines.append(
                f"- {failure['id']}: {humanize(failure['action'])}; "
                f"{', '.join(failure['failures'])}"
            )
    else:
        lines.append("- No expectation failures.")

    lines.extend(["", "## Cases", ""])
    for item in report["results"]:
        dimensions = ", ".join(humanize(value) for value in item.get("dimensions", []))
        lines.append(
            f"- {item['id']}: {humanize(item['action'])}; "
            f"passed={item['passed_expectations']}; dimensions={dimensions}"
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Production-hardening evals for crypto scam moderation.")
    parser.add_argument("--cases", default=str(ROOT / "evals" / "hardening_eval_cases.json"))
    parser.add_argument("--model-path", default=str(ROOT / "audit_outputs" / "fraud_labeler_v2.joblib"))
    parser.add_argument("--out", default=str(ROOT / "audit_outputs" / "production_hardening_eval_report.json"))
    parser.add_argument("--markdown-out", default=str(ROOT / "audit_outputs" / "production_hardening_eval_report.md"))
    parser.add_argument("--lab-summary", default=str(ROOT / "crypto-scam-lab" / "data" / "hardeningSummary.js"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    model, thresholds = load_artifact(Path(args.model_path))
    results = [augment_result(score_case(case, model, thresholds)) for case in cases]
    report = build_report(results, thresholds)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    write_markdown(Path(args.markdown_out), report)
    summary = compact_lab_summary(report)
    write_lab_summary(Path(args.lab_summary), summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
