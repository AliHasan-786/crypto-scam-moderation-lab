from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


NOTICE_TEMPLATES = [
    {
        "id": "potential_crypto_fraud_label",
        "title": "Potential Crypto Fraud label notice",
        "trigger": "Reviewer confirms concrete scam evidence.",
        "body": (
            "We added a Potential Crypto Fraud label because the post appears to request crypto, "
            "wallet connection, or payment using scam-like claims. You can appeal if context is missing."
        ),
        "includedFields": ["policy rule", "matched evidence", "appeal link", "automation disclosure"],
    },
    {
        "id": "high_confidence_escalation",
        "title": "Escalation notice",
        "trigger": "High-risk wallet, domain, or impersonation evidence requires deeper review.",
        "body": (
            "This post was escalated for additional review because it combines high-risk crypto-scam "
            "signals such as wallet requests, impersonation, urgency, or repeated campaign infrastructure."
        ),
        "includedFields": ["escalation reason", "review status", "appeal/feedback path"],
    },
    {
        "id": "appeal_received",
        "title": "Appeal received notice",
        "trigger": "A user challenges a label or moderation decision.",
        "body": (
            "We received your appeal. A reviewer will check the original evidence, your added context, "
            "and whether the post falls into a protected context such as warning, research, satire, or help-seeking."
        ),
        "includedFields": ["case id", "expected review window", "what reviewers check"],
    },
    {
        "id": "reversal_notice",
        "title": "Reversal notice",
        "trigger": "Reviewer finds the original action was not warranted.",
        "body": (
            "We removed the label after review. The post does not meet the Potential Crypto Fraud standard "
            "under the available context."
        ),
        "includedFields": ["reversal reason", "false-positive category", "recorded outcome"],
    },
]


STANDARDS_CONTROLS = [
    {
        "id": "clear_rules",
        "standard": "Santa Clara Principles",
        "control": "Clear public rule and boundary examples",
        "evidence": "Policy boundary card, scenario eval cases, and notice templates.",
        "status": "implemented",
        "score": 1.0,
    },
    {
        "id": "appealability",
        "standard": "Santa Clara Principles",
        "control": "Appeal path and reversal tracking",
        "evidence": "Appeal scenarios, reversed outcomes, and review-store statuses for appealed/reversed items.",
        "status": "implemented",
        "score": 0.9,
    },
    {
        "id": "measure_risk",
        "standard": "NIST AI RMF Measure",
        "control": "Measure false positives, ambiguity routing, and reviewer-action distribution",
        "evidence": "Scenario evals, evidence-extractor evals, adversarial lab, and transparency report metrics.",
        "status": "implemented",
        "score": 1.0,
    },
    {
        "id": "manage_risk",
        "standard": "NIST AI RMF Manage",
        "control": "Route uncertainty to humans before public enforcement",
        "evidence": "Human-review tier, missing-context evidence field, and recovery-service appeal scenario.",
        "status": "implemented",
        "score": 0.95,
    },
    {
        "id": "detect_respond",
        "standard": "NIST CSF 2.0",
        "control": "Detect scam campaigns and respond through review/escalation",
        "evidence": "SQLite review store, entity extraction, campaign graph, and escalation status.",
        "status": "implemented",
        "score": 0.85,
    },
    {
        "id": "llm_agency_boundary",
        "standard": "OWASP LLM / Agentic AI",
        "control": "Constrain LLM output to evidence assistance, not autonomous action",
        "evidence": "Structured evidence schema, span-faithfulness evals, and no publishing capability.",
        "status": "implemented",
        "score": 0.95,
    },
    {
        "id": "privacy_retention",
        "standard": "Trust & Safety Operations",
        "control": "Limit public demo data and keep live samples local",
        "evidence": "Sanitized demo queue and read-only Bluesky ingestion scaffolds.",
        "status": "partial",
        "score": 0.75,
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_rows(db_path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not db_path.exists():
        return [], []
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        items = [dict(row) for row in connection.execute("SELECT * FROM review_items").fetchall()]
        events = [dict(row) for row in connection.execute("SELECT * FROM review_events").fetchall()]
        return items, events
    finally:
        connection.close()


def rate(numerator: int | float, denominator: int | float) -> float:
    return float(numerator) / max(1.0, float(denominator))


def false_positive_category(text: str, notes: str = "") -> str:
    lowered = f"{text} {notes}".lower()
    if "do not send" in lowered or "warning" in lowered or "warn" in lowered:
        return "consumer_warning"
    if "satire" in lowered or "joke" in lowered or "imaginary" in lowered or "obviously not" in lowered:
        return "satire"
    if "research" in lowered or "paper" in lowered or "study" in lowered:
        return "research"
    if "does anyone" in lowered or "has anyone" in lowered or "safely" in lowered:
        return "help_seeking"
    if "earnings" in lowered or "analyst" in lowered or "revenue" in lowered:
        return "market_news"
    return "other_context"


def queue_metrics(items: list[dict[str, Any]], events: list[dict[str, Any]]) -> dict[str, Any]:
    statuses = Counter(str(item.get("status") or "unknown") for item in items)
    decisions = Counter(str(item.get("reviewer_decision") or "none") for item in items)
    event_counts = Counter(str(event.get("event_type") or "unknown") for event in events)

    reviewed_items = [
        item
        for item in items
        if item.get("status") != "new" or item.get("reviewer_decision") not in (None, "", "none")
    ]
    actioned_items = [
        item
        for item in items
        if item.get("status") in {"labeled", "escalated"} or item.get("reviewer_decision") == "fraud"
    ]
    appealed_items = [
        item
        for item in items
        if item.get("status") == "appealed" or str(item.get("reviewer_decision") or "").startswith("appeal_")
    ]
    reversed_items = [
        item
        for item in items
        if item.get("status") == "reversed" or item.get("reviewer_decision") == "appeal_reversed"
    ]
    dismissed_not_fraud = [
        item
        for item in items
        if item.get("status") == "dismissed" or item.get("reviewer_decision") in {"not_fraud", "appeal_reversed"}
    ]
    false_positive_counts = Counter(
        false_positive_category(str(item.get("text") or ""), str(item.get("reviewer_notes") or ""))
        for item in dismissed_not_fraud
    )

    return {
        "totalCandidates": len(items),
        "reviewedOrTriaged": len(reviewed_items),
        "actioned": len(actioned_items),
        "labeled": statuses.get("labeled", 0),
        "escalated": statuses.get("escalated", 0),
        "dismissed": statuses.get("dismissed", 0),
        "appealed": len(appealed_items),
        "reversed": len(reversed_items),
        "automationAssistedRate": rate(sum(1 for item in items if item.get("probability") is not None), len(items)),
        "reviewAutomationAssistedRate": rate(
            sum(1 for item in reviewed_items if item.get("probability") is not None),
            len(reviewed_items),
        ),
        "statusCounts": dict(sorted(statuses.items())),
        "decisionCounts": dict(sorted(decisions.items())),
        "eventCounts": dict(sorted(event_counts.items())),
        "falsePositiveCategories": dict(sorted(false_positive_counts.items())),
    }


def appeal_metrics(scenarios: list[dict[str, Any]]) -> dict[str, Any]:
    submitted = [scenario for scenario in scenarios if scenario.get("appealSubmitted")]
    reversed_cases = [scenario for scenario in submitted if scenario.get("reversed")]
    upheld = [scenario for scenario in submitted if scenario.get("finalOutcome") == "upheld"]
    clarification = [scenario for scenario in submitted if scenario.get("finalOutcome") == "clarification_sent"]
    category_counts = Counter(
        scenario.get("falsePositiveCategory") or "not_false_positive"
        for scenario in submitted
    )
    bucket_counts = Counter(str(scenario.get("transparencyBucket") or "unknown") for scenario in scenarios)

    return {
        "scenarioCount": len(scenarios),
        "submitted": len(submitted),
        "reversed": len(reversed_cases),
        "upheld": len(upheld),
        "clarificationOnly": len(clarification),
        "reversalRate": rate(len(reversed_cases), len(submitted)),
        "falsePositiveCategories": dict(sorted(category_counts.items())),
        "transparencyBuckets": dict(sorted(bucket_counts.items())),
    }


def scorecard_summary(controls: list[dict[str, Any]]) -> dict[str, Any]:
    implemented = [control for control in controls if control["status"] == "implemented"]
    average_score = sum(float(control["score"]) for control in controls) / max(1, len(controls))
    return {
        "controlCount": len(controls),
        "implementedCount": len(implemented),
        "partialCount": sum(1 for control in controls if control["status"] == "partial"),
        "averageScore": round(average_score, 3),
    }


def compact_scenario(scenario: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": scenario["id"],
        "title": scenario["title"],
        "initialAction": scenario["initialAction"],
        "appealClaim": scenario["appealClaim"],
        "finalOutcome": scenario["finalOutcome"],
        "reversed": bool(scenario["reversed"]),
        "falsePositiveCategory": scenario.get("falsePositiveCategory"),
        "reviewerChecks": scenario.get("reviewerChecks", [])[:3],
        "userNotice": scenario["userNotice"],
    }


def build_report(db_path: Path, scenarios_path: Path) -> dict[str, Any]:
    items, events = fetch_rows(db_path)
    scenarios = load_json(scenarios_path)
    queue = queue_metrics(items, events)
    appeals = appeal_metrics(scenarios)
    scorecard = scorecard_summary(STANDARDS_CONTROLS)

    return {
        "generatedAt": utc_now(),
        "suite": "governance_transparency_v1",
        "dbPath": str(db_path),
        "scenarioPath": str(scenarios_path),
        "caveat": (
            "Operational queue metrics come from the local SQLite review store. Appeal examples are authored, "
            "sanitized portfolio scenarios that exercise notice, appeal, and reversal flows without using live user data."
        ),
        "queueMetrics": queue,
        "appealMetrics": appeals,
        "transparencyMetrics": {
            "totalReviewed": queue["reviewedOrTriaged"],
            "totalActioned": queue["actioned"],
            "totalAppealedInQueue": queue["appealed"],
            "totalReversedInQueue": queue["reversed"],
            "authoredAppealScenarios": appeals["scenarioCount"],
            "authoredReversals": appeals["reversed"],
            "automationAssistedRate": queue["automationAssistedRate"],
            "reviewAutomationAssistedRate": queue["reviewAutomationAssistedRate"],
        },
        "noticeTemplates": NOTICE_TEMPLATES,
        "appealScenarios": scenarios,
        "standardsScorecard": {
            "summary": scorecard,
            "controls": STANDARDS_CONTROLS,
        },
    }


def lab_summary(report: dict[str, Any]) -> dict[str, Any]:
    controls = report["standardsScorecard"]["controls"]
    return {
        "generatedAt": report["generatedAt"],
        "suite": report["suite"],
        "caveat": report["caveat"],
        "queueMetrics": report["queueMetrics"],
        "appealMetrics": report["appealMetrics"],
        "transparencyMetrics": report["transparencyMetrics"],
        "noticeTemplates": report["noticeTemplates"][:3],
        "appealScenarios": [compact_scenario(scenario) for scenario in report["appealScenarios"][:4]],
        "standardsScorecard": {
            "summary": report["standardsScorecard"]["summary"],
            "controls": controls[:6],
        },
    }


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_markdown(report: dict[str, Any]) -> str:
    queue = report["queueMetrics"]
    appeals = report["appealMetrics"]
    scorecard = report["standardsScorecard"]["summary"]
    lines = [
        "# Governance And Transparency Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        "## Summary",
        "",
        f"- Local queue candidates: {queue['totalCandidates']}",
        f"- Reviewed or triaged: {queue['reviewedOrTriaged']}",
        f"- Actioned in queue: {queue['actioned']}",
        f"- Authored appeal scenarios: {appeals['scenarioCount']}",
        f"- Authored appeal reversal rate: {pct(appeals['reversalRate'])}",
        f"- Automation-assisted queue rate: {pct(queue['automationAssistedRate'])}",
        f"- Standards average score: {scorecard['averageScore']:.3f}",
        "",
        "Interpretation: this report separates local operational metrics from authored appeal scenarios. The authored scenarios demonstrate due process, notice quality, and reversal handling without publishing or storing live platform user content.",
        "",
        "## Queue Snapshot",
        "",
    ]
    for key, value in queue["statusCounts"].items():
        lines.append(f"- {key}: {value}")
    lines.extend(["", "## Appeal Scenarios", ""])
    for scenario in report["appealScenarios"]:
        outcome = "reversed" if scenario["reversed"] else scenario["finalOutcome"]
        lines.extend(
            [
                f"### {scenario['title']}",
                "",
                f"- Initial action: {scenario['initialAction']}",
                f"- Appeal claim: {scenario['appealClaim']}",
                f"- Outcome: {outcome}",
                f"- User notice: {scenario['userNotice']}",
                "",
            ]
        )
    lines.extend(["## Notice Templates", ""])
    for template in report["noticeTemplates"]:
        lines.extend(
            [
                f"### {template['title']}",
                "",
                f"- Trigger: {template['trigger']}",
                f"- Body: {template['body']}",
                "",
            ]
        )
    lines.extend(["## Standards Scorecard", ""])
    for control in report["standardsScorecard"]["controls"]:
        lines.append(
            f"- {control['standard']} / {control['control']}: {control['status']} ({float(control['score']):.2f})"
        )
    lines.extend(
        [
            "",
            "## Caveat",
            "",
            report["caveat"],
            "",
        ]
    )
    return "\n".join(lines)


def write_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_lab(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, ensure_ascii=False, indent=2)
    path.write_text(f"export const governanceReport = {rendered};\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate governance, appeal, and transparency artifacts.")
    parser.add_argument("--db", default=str(ROOT / "audit_outputs" / "live_review_queue.sqlite"))
    parser.add_argument("--scenarios", default=str(ROOT / "governance" / "appeal_scenarios.json"))
    parser.add_argument("--out", default=str(ROOT / "audit_outputs" / "governance_transparency_report.json"))
    parser.add_argument("--markdown-out", default=str(ROOT / "audit_outputs" / "governance_transparency_report.md"))
    parser.add_argument("--lab-summary", default=str(ROOT / "crypto-scam-lab" / "data" / "governanceReport.js"))
    args = parser.parse_args()

    report = build_report(Path(args.db), Path(args.scenarios))
    write_json(Path(args.out), report)
    Path(args.markdown_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.markdown_out).write_text(render_markdown(report), encoding="utf-8")
    summary = lab_summary(report)
    write_lab(Path(args.lab_summary), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
