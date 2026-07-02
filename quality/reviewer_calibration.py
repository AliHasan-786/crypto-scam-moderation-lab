from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def load_cases(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def generate_report(cases: list[dict]) -> dict:
    action_counts = Counter(case["expected_action"] for case in cases)
    decision_counts = Counter(case["expected_decision"] for case in cases)
    severity_counts = Counter(case["severity"] for case in cases)
    focus_counts = Counter(case["policy_focus"] for case in cases)

    protected_focuses = {
        "consumer_warning",
        "market_news",
        "developer_context",
        "satire",
        "multilingual_help_seeking",
        "ocr_source_ambiguity",
        "redirect_mismatch",
    }
    fraud_cases = [case for case in cases if case["expected_decision"] == "fraud"]
    review_cases = [case for case in cases if case["expected_action"] == "human_review"]
    no_label_cases = [case for case in cases if case["expected_action"] == "no_label"]
    protected_context_cases = [
        case for case in cases if case["policy_focus"] in protected_focuses
    ]

    by_action = defaultdict(list)
    for case in cases:
        by_action[case["expected_action"]].append(case["id"])

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "suite": "reviewer_calibration_v1",
        "caseCount": len(cases),
        "actionCounts": dict(action_counts),
        "decisionCounts": dict(decision_counts),
        "severityCounts": dict(severity_counts),
        "policyFocusCounts": dict(focus_counts),
        "fraudCaseCount": len(fraud_cases),
        "reviewCaseCount": len(review_cases),
        "noLabelCaseCount": len(no_label_cases),
        "protectedContextCaseCount": len(protected_context_cases),
        "coverage": {
            "publicLabelCases": len(by_action["public_label"]),
            "humanReviewCases": len(by_action["human_review"]),
            "noLabelCases": len(by_action["no_label"]),
            "multilingualCases": sum(1 for case in cases if "spanish" in case["id"] or "multilingual" in case["policy_focus"]),
            "urlOrRedirectCases": sum(1 for case in cases if any(term in case["policy_focus"] for term in ["shortener", "redirect", "wallet_drainer"])),
            "protectedContextCases": len(protected_context_cases),
        },
        "calibrationStandards": [
            "Reviewer must cite concrete evidence for public labels.",
            "Reviewer must identify protected context before applying public labels.",
            "Suspicious but incomplete cases should route to human review.",
            "Reviewer notes should be specific enough for appeal and QA review.",
            "Repeated calibration misses should become policy guidance or eval cases.",
        ],
        "recommendedQAProcess": [
            "Run calibration before reviewer launch and after policy updates.",
            "Score each reviewer against expected action, evidence quality, and context sensitivity.",
            "Review disagreement cases in group calibration.",
            "Promote common misses into evals and training examples.",
            "Track false-positive and false-negative themes over time.",
        ],
        "cases": cases,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Reviewer Calibration Report",
        "",
        f"Generated: `{report['generatedAt']}`",
        "",
        "## Summary",
        "",
        f"- Calibration cases: **{report['caseCount']}**",
        f"- Public-label answer-key cases: **{report['coverage']['publicLabelCases']}**",
        f"- Human-review answer-key cases: **{report['coverage']['humanReviewCases']}**",
        f"- No-label answer-key cases: **{report['coverage']['noLabelCases']}**",
        f"- Protected-context cases: **{report['protectedContextCaseCount']}**",
        f"- Multilingual cases: **{report['coverage']['multilingualCases']}**",
        f"- URL/redirect/wallet-drainer cases: **{report['coverage']['urlOrRedirectCases']}**",
        "",
        "## Action Distribution",
        "",
    ]
    for action, count in sorted(report["actionCounts"].items()):
        lines.append(f"- `{action}`: {count}")

    lines.extend(["", "## QA Standards", ""])
    for standard in report["calibrationStandards"]:
        lines.append(f"- {standard}")

    lines.extend(["", "## Recommended QA Process", ""])
    for step in report["recommendedQAProcess"]:
        lines.append(f"- {step}")

    lines.extend(["", "## Calibration Cases", ""])
    for case in report["cases"]:
        lines.extend(
            [
                f"### {case['id']}",
                "",
                f"- Expected action: `{case['expected_action']}`",
                f"- Expected decision: `{case['expected_decision']}`",
                f"- Policy focus: `{case['policy_focus']}`",
                f"- Severity: `{case['severity']}`",
                f"- Rationale: {case['rationale']}",
                "",
            ]
        )
    return "\n".join(lines)


def write_lab_summary(report: dict, path: str | Path) -> None:
    lab = {
        "generatedAt": report["generatedAt"],
        "caseCount": report["caseCount"],
        "coverage": report["coverage"],
        "actionCounts": report["actionCounts"],
        "severityCounts": report["severityCounts"],
        "policyFocusCounts": report["policyFocusCounts"],
        "calibrationStandards": report["calibrationStandards"],
        "recommendedQAProcess": report["recommendedQAProcess"],
        "sampleCases": report["cases"][:6],
    }
    output = "export const qualityCalibration = " + json.dumps(lab, indent=2, ensure_ascii=False) + ";\n"
    Path(path).write_text(output, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate reviewer calibration artifacts.")
    parser.add_argument("--cases", default="quality/calibration_cases.json")
    parser.add_argument("--out", default="audit_outputs/reviewer_calibration_report.json")
    parser.add_argument("--markdown-out", default="audit_outputs/reviewer_calibration_report.md")
    parser.add_argument("--lab-summary", default="crypto-scam-lab/data/qualityCalibration.js")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    report = generate_report(cases)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.markdown_out).write_text(render_markdown(report), encoding="utf-8")
    write_lab_summary(report, args.lab_summary)
    print(json.dumps({"caseCount": report["caseCount"], "coverage": report["coverage"]}, indent=2))


if __name__ == "__main__":
    main()
