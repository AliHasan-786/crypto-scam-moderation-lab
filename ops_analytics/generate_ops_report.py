from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def row_dicts(rows: list[sqlite3.Row]) -> list[dict]:
    return [dict(row) for row in rows]


def pct(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def connect(db_path: str | Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def fetch_one(connection: sqlite3.Connection, query: str, params: tuple = ()) -> dict:
    row = connection.execute(query, params).fetchone()
    return dict(row) if row else {}


def fetch_all(connection: sqlite3.Connection, query: str, params: tuple = ()) -> list[dict]:
    return row_dicts(connection.execute(query, params).fetchall())


def generate_report(db_path: str | Path) -> dict:
    with connect(db_path) as connection:
        totals = fetch_one(
            connection,
            """
            SELECT
              COUNT(*) AS total_items,
              SUM(CASE WHEN reviewer_decision IS NOT NULL THEN 1 ELSE 0 END) AS reviewed_items,
              SUM(CASE WHEN reviewer_decision IS NULL THEN 1 ELSE 0 END) AS unreviewed_items,
              SUM(CASE WHEN status IN ('escalated', 'labeled') THEN 1 ELSE 0 END) AS actioned_items,
              SUM(CASE WHEN status = 'dismissed' OR reviewer_decision = 'not_fraud' THEN 1 ELSE 0 END) AS dismissed_items,
              SUM(duplicate_count) AS total_observations,
              ROUND(AVG(probability), 4) AS avg_probability
            FROM review_items
            """,
        )
        total_items = int(totals.get("total_items") or 0)
        reviewed_items = int(totals.get("reviewed_items") or 0)
        unreviewed_items = int(totals.get("unreviewed_items") or 0)
        actioned_items = int(totals.get("actioned_items") or 0)
        dismissed_items = int(totals.get("dismissed_items") or 0)

        status_counts = fetch_all(
            connection,
            """
            SELECT status, COUNT(*) AS count
            FROM review_items
            GROUP BY status
            ORDER BY count DESC, status
            """,
        )
        action_counts = fetch_all(
            connection,
            """
            SELECT action, COUNT(*) AS count, ROUND(AVG(probability), 4) AS avg_probability
            FROM review_items
            GROUP BY action
            ORDER BY count DESC, action
            """,
        )
        decision_counts = fetch_all(
            connection,
            """
            SELECT COALESCE(reviewer_decision, 'unreviewed') AS decision, COUNT(*) AS count
            FROM review_items
            GROUP BY COALESCE(reviewer_decision, 'unreviewed')
            ORDER BY count DESC, decision
            """,
        )
        event_counts = fetch_all(
            connection,
            """
            SELECT event_type, COUNT(*) AS count
            FROM review_events
            GROUP BY event_type
            ORDER BY count DESC, event_type
            """,
        )
        false_positive_candidates = fetch_all(
            connection,
            """
            SELECT
              uri,
              author_handle,
              ROUND(probability, 4) AS probability,
              action,
              status,
              reviewer_decision,
              reviewer_notes,
              substr(text, 1, 180) AS text_preview
            FROM review_items
            WHERE status = 'dismissed' OR reviewer_decision = 'not_fraud'
            ORDER BY probability DESC
            LIMIT 10
            """,
        )
        backlog_items = fetch_all(
            connection,
            """
            SELECT
              uri,
              author_handle,
              ROUND(probability, 4) AS probability,
              action,
              status,
              duplicate_count,
              substr(text, 1, 180) AS text_preview
            FROM review_items
            WHERE reviewer_decision IS NULL
            ORDER BY
              CASE action
                WHEN 'high_confidence_escalation' THEN 1
                WHEN 'apply_potential_crypto_fraud_label' THEN 2
                WHEN 'send_to_human_review' THEN 3
                ELSE 4
              END,
              probability DESC
            LIMIT 10
            """,
        )
        top_entities = fetch_all(
            connection,
            """
            SELECT
              e.entity_type,
              e.value,
              e.observation_count,
              ROUND(e.max_risk_weight, 4) AS max_risk_weight,
              COUNT(ie.uri) AS linked_items
            FROM review_entities e
            JOIN review_item_entities ie ON e.entity_id = ie.entity_id
            GROUP BY e.entity_id, e.entity_type, e.value, e.observation_count, e.max_risk_weight
            ORDER BY linked_items DESC, e.max_risk_weight DESC, e.value
            LIMIT 12
            """,
        )
        source_counts = fetch_all(
            connection,
            """
            SELECT source, COUNT(*) AS count
            FROM review_items
            GROUP BY source
            ORDER BY count DESC, source
            """,
        )

    review_coverage = pct(reviewed_items, total_items)
    backlog_rate = pct(unreviewed_items, total_items)
    action_rate = pct(actioned_items, total_items)
    dismissal_rate = pct(dismissed_items, reviewed_items)

    risk_notes = []
    if unreviewed_items:
        risk_notes.append("Backlog exists; prioritize unresolved items by action tier, probability, duplicate count, and shared entities.")
    if false_positive_candidates:
        risk_notes.append("Dismissed/not-fraud cases should feed policy clarification and false-positive evals.")
    if top_entities:
        risk_notes.append("Repeated entities are useful campaign leads, but should not trigger enforcement without content and context review.")
    if reviewed_items:
        risk_notes.append("Reviewer decisions create an active-learning and QA feedback loop.")

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "dbPath": str(db_path),
        "summary": {
            "totalItems": total_items,
            "reviewedItems": reviewed_items,
            "unreviewedItems": unreviewed_items,
            "actionedItems": actioned_items,
            "dismissedItems": dismissed_items,
            "totalObservations": int(totals.get("total_observations") or 0),
            "avgProbability": float(totals.get("avg_probability") or 0.0),
            "reviewCoverage": review_coverage,
            "backlogRate": backlog_rate,
            "actionRate": action_rate,
            "dismissalRateAmongReviewed": dismissal_rate,
        },
        "statusCounts": status_counts,
        "actionCounts": action_counts,
        "decisionCounts": decision_counts,
        "sourceCounts": source_counts,
        "eventCounts": event_counts,
        "falsePositiveCandidates": false_positive_candidates,
        "backlogItems": backlog_items,
        "topEntities": top_entities,
        "riskNotes": risk_notes,
        "operationalQuestions": [
            "SQL-readable queue health and reviewer decision metrics.",
            "False-positive and backlog examples for policy review.",
            "Entity leaderboard for fraud-intelligence and campaign triage.",
            "Event history for auditability and process improvement.",
        ],
    }


def render_markdown(report: dict) -> str:
    summary = report["summary"]
    lines = [
        "# Trust & Safety Ops Analytics Report",
        "",
        f"Generated: `{report['generatedAt']}`",
        "",
        "## Executive Summary",
        "",
        f"- Total queue items: **{summary['totalItems']}**",
        f"- Reviewed items: **{summary['reviewedItems']}**",
        f"- Unreviewed backlog: **{summary['unreviewedItems']}**",
        f"- Review coverage: **{summary['reviewCoverage']:.1%}**",
        f"- Action rate: **{summary['actionRate']:.1%}**",
        f"- Dismissal rate among reviewed items: **{summary['dismissalRateAmongReviewed']:.1%}**",
        f"- Total observations after duplicate refreshes: **{summary['totalObservations']}**",
        "",
        "## Status Counts",
        "",
    ]
    for item in report["statusCounts"]:
        lines.append(f"- `{item['status']}`: {item['count']}")

    lines.extend(["", "## Reviewer Decisions", ""])
    for item in report["decisionCounts"]:
        lines.append(f"- `{item['decision']}`: {item['count']}")

    lines.extend(["", "## Action Tiers", ""])
    for item in report["actionCounts"]:
        lines.append(f"- `{item['action']}`: {item['count']} items, avg probability {item['avg_probability']}")

    lines.extend(["", "## Backlog Candidates", ""])
    if report["backlogItems"]:
        for item in report["backlogItems"]:
            lines.append(
                f"- `{item['action']}` / p={item['probability']}: {item['text_preview']}"
            )
    else:
        lines.append("- No unresolved items.")

    lines.extend(["", "## False-Positive Candidates", ""])
    if report["falsePositiveCandidates"]:
        for item in report["falsePositiveCandidates"]:
            lines.append(
                f"- `{item['reviewer_decision']}` / p={item['probability']}: {item['text_preview']}"
            )
    else:
        lines.append("- No dismissed/not-fraud reviewed items in the current queue.")

    lines.extend(["", "## Entity Leads", ""])
    for entity in report["topEntities"]:
        lines.append(
            f"- `{entity['entity_type']}` `{entity['value']}`: {entity['linked_items']} linked items, max risk {entity['max_risk_weight']}"
        )

    lines.extend(["", "## Operational Questions", ""])
    for question in report["operationalQuestions"]:
        lines.append(f"- {question}")

    lines.extend(["", "## Analyst Notes", ""])
    for note in report["riskNotes"]:
        lines.append(f"- {note}")

    return "\n".join(lines) + "\n"


def write_lab_summary(report: dict, path: str | Path) -> None:
    summary = report["summary"]
    lab = {
        "generatedAt": report["generatedAt"],
        "summary": summary,
        "statusCounts": report["statusCounts"],
        "decisionCounts": report["decisionCounts"],
        "actionCounts": report["actionCounts"],
        "topEntities": report["topEntities"][:6],
        "backlogItems": report["backlogItems"][:4],
        "falsePositiveCandidates": report["falsePositiveCandidates"][:4],
        "riskNotes": report["riskNotes"],
    }
    output = "export const opsAnalytics = " + json.dumps(lab, indent=2, ensure_ascii=False) + ";\n"
    Path(path).write_text(output, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Trust & Safety ops analytics from the local review queue.")
    parser.add_argument("--db", default="audit_outputs/live_review_queue.sqlite")
    parser.add_argument("--out", default="audit_outputs/ops_analytics_report.json")
    parser.add_argument("--markdown-out", default="audit_outputs/ops_analytics_report.md")
    parser.add_argument("--lab-summary", default="crypto-scam-lab/data/opsAnalytics.js")
    args = parser.parse_args()

    report = generate_report(args.db)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.markdown_out).write_text(render_markdown(report), encoding="utf-8")
    write_lab_summary(report, args.lab_summary)
    print(json.dumps(report["summary"], indent=2))


if __name__ == "__main__":
    main()
