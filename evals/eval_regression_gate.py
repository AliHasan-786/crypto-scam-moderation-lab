from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def get_path(data: dict, path: list[str], default: Any = None) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def check(name: str, value: float, threshold: float, comparator: str = ">=") -> dict:
    if comparator == ">=":
        passed = value >= threshold
    elif comparator == "<=":
        passed = value <= threshold
    else:
        raise ValueError(f"Unsupported comparator: {comparator}")
    return {
        "name": name,
        "value": value,
        "threshold": threshold,
        "comparator": comparator,
        "passed": passed,
    }


def generate_report(args: argparse.Namespace) -> dict:
    eval_suite = read_json(args.eval_suite)
    hardening = read_json(args.hardening)
    adversarial = read_json(args.adversarial)
    evidence = read_json(args.evidence)
    governance = read_json(args.governance)
    ops = read_json(args.ops)
    calibration = read_json(args.calibration)
    incident = read_json(args.incident)

    governance_avg = float(
        get_path(governance, ["standardsScorecard", "averageScore"], 0)
        or get_path(governance, ["standards_scorecard", "average_score"], 0)
        or get_path(governance, ["summary", "standardsScorecardAverage"], 0)
        or 0
    )
    evidence_faithfulness = float(
        get_path(evidence, ["faithfulnessRate"], 0)
        or get_path(evidence, ["spanFaithfulnessRate"], 0)
        or get_path(evidence, ["summary", "spanFaithfulnessRate"], 0)
        or 0
    )
    if evidence_faithfulness > 1:
        evidence_faithfulness = evidence_faithfulness / 100

    checks = [
        check("scenario expectation pass rate", float(eval_suite.get("expectation_pass_rate", 0)), 1.0),
        check("scenario public-label precision", float(get_path(eval_suite, ["binary_metrics", "public_label", "precision"], 0)), 0.95),
        check("scenario review-or-label recall", float(get_path(eval_suite, ["binary_metrics", "review_or_label", "recall"], 0)), 1.0),
        check("hardening expectation pass rate", float(hardening.get("expectationPassRate", 0)), 1.0),
        check("hardening legitimate no-public-label rate", float(hardening.get("legitimateNoPublicLabelRate", 0)), 1.0),
        check("adversarial review-or-label retention", float(adversarial.get("reviewOrLabelRetentionRate", 0)), 1.0),
        check("adversarial escape rate", float(adversarial.get("escapeRate", 1)), 0.0, "<="),
        check("evidence span faithfulness", evidence_faithfulness, 1.0),
        check("ops review coverage demo floor", float(get_path(ops, ["summary", "reviewCoverage"], 0)), 0.5),
        check("calibration case count", float(calibration.get("caseCount", 0)), 12),
        check("incident tabletop scenario count", float(incident.get("scenarioCount", 0)), 3),
    ]
    if governance_avg:
        checks.append(check("governance standards score average", governance_avg, 0.85))

    failed = [item for item in checks if not item["passed"]]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "suite": "trust_safety_portfolio_regression_gate_v1",
        "passed": not failed,
        "checkCount": len(checks),
        "failedCount": len(failed),
        "checks": checks,
        "failedChecks": failed,
        "purpose": "This gate protects false-positive control, review routing, evidence faithfulness, calibration coverage, and incident readiness.",
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Trust & Safety Regression Gate",
        "",
        f"Generated: `{report['generatedAt']}`",
        "",
        f"Overall result: **{'PASS' if report['passed'] else 'FAIL'}**",
        "",
        f"- Checks: **{report['checkCount']}**",
        f"- Failed checks: **{report['failedCount']}**",
        "",
        "## Checks",
        "",
    ]
    for item in report["checks"]:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(
            f"- **{status}** `{item['name']}`: {item['value']} {item['comparator']} {item['threshold']}"
        )
    lines.extend(["", "## Why This Gate Exists", "", report["purpose"], ""])
    return "\n".join(lines)


def write_lab_summary(report: dict, path: str | Path) -> None:
    lab = {
        "generatedAt": report["generatedAt"],
        "passed": report["passed"],
        "checkCount": report["checkCount"],
        "failedCount": report["failedCount"],
        "checks": report["checks"],
        "failedChecks": report["failedChecks"],
        "purpose": report["purpose"],
    }
    output = "export const evalGate = " + json.dumps(lab, indent=2, ensure_ascii=False) + ";\n"
    Path(path).write_text(output, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run portfolio-level Trust & Safety regression gates.")
    parser.add_argument("--eval-suite", default="audit_outputs/eval_suite_report.json")
    parser.add_argument("--hardening", default="audit_outputs/production_hardening_eval_report.json")
    parser.add_argument("--adversarial", default="audit_outputs/adversarial_scam_lab_report.json")
    parser.add_argument("--evidence", default="audit_outputs/llm_evidence_report.json")
    parser.add_argument("--governance", default="audit_outputs/governance_transparency_report.json")
    parser.add_argument("--ops", default="audit_outputs/ops_analytics_report.json")
    parser.add_argument("--calibration", default="audit_outputs/reviewer_calibration_report.json")
    parser.add_argument("--incident", default="audit_outputs/incident_response_tabletop.json")
    parser.add_argument("--out", default="audit_outputs/eval_regression_gate_report.json")
    parser.add_argument("--markdown-out", default="audit_outputs/eval_regression_gate_report.md")
    parser.add_argument("--lab-summary", default="crypto-scam-lab/data/evalGate.js")
    args = parser.parse_args()

    report = generate_report(args)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.markdown_out).write_text(render_markdown(report), encoding="utf-8")
    write_lab_summary(report, args.lab_summary)
    print(json.dumps({"passed": report["passed"], "failedCount": report["failedCount"]}, indent=2))
    if not report["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
