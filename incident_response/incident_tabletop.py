from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


SEVERITY_RANK = {"sev1": 4, "sev2": 3, "sev3": 2, "sev4": 1}


def load_scenarios(path: str | Path) -> list[dict]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def generate_report(scenarios: list[dict]) -> dict:
    severity_counts = Counter(scenario["severity"] for scenario in scenarios)
    partner_counts = Counter(
        partner
        for scenario in scenarios
        for partner in scenario.get("cross_functional_partners", [])
    )
    metric_counts = Counter(
        metric
        for scenario in scenarios
        for metric in scenario.get("success_metrics", [])
    )
    top_scenario = max(scenarios, key=lambda item: SEVERITY_RANK.get(item["severity"], 0))
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "suite": "crypto_scam_incident_tabletop_v1",
        "scenarioCount": len(scenarios),
        "severityCounts": dict(severity_counts),
        "partnerCounts": dict(partner_counts),
        "metricCounts": dict(metric_counts),
        "highestSeverityScenario": {
            "id": top_scenario["id"],
            "title": top_scenario["title"],
            "severity": top_scenario["severity"],
        },
        "operatingPrinciples": [
            "Preserve evidence before broad enforcement changes.",
            "Route ambiguity to review instead of forcing a public label.",
            "Use shared entities as campaign leads, not standalone proof.",
            "Convert incidents into eval, policy, QA, or tooling updates.",
            "Track false-positive impact alongside fraud mitigation.",
        ],
        "scenarios": scenarios,
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# Crypto Scam Incident Tabletop Report",
        "",
        f"Generated: `{report['generatedAt']}`",
        "",
        "## Summary",
        "",
        f"- Scenarios: **{report['scenarioCount']}**",
        f"- Highest severity scenario: **{report['highestSeverityScenario']['title']}** (`{report['highestSeverityScenario']['severity']}`)",
        "",
        "## Operating Principles",
        "",
    ]
    for principle in report["operatingPrinciples"]:
        lines.append(f"- {principle}")

    lines.extend(["", "## Scenario Details", ""])
    for scenario in report["scenarios"]:
        lines.extend(
            [
                f"### {scenario['title']}",
                "",
                f"- ID: `{scenario['id']}`",
                f"- Severity: `{scenario['severity']}`",
                f"- Trigger: {scenario['trigger']}",
                "",
                "First actions:",
            ]
        )
        for action in scenario["first_actions"]:
            lines.append(f"- {action}")
        lines.append("")
        lines.append("Mitigations:")
        for mitigation in scenario["mitigations"]:
            lines.append(f"- {mitigation}")
        lines.append("")
        lines.append("Success metrics:")
        for metric in scenario["success_metrics"]:
            lines.append(f"- {metric}")
        lines.append("")

    return "\n".join(lines)


def write_lab_summary(report: dict, path: str | Path) -> None:
    lab = {
        "generatedAt": report["generatedAt"],
        "scenarioCount": report["scenarioCount"],
        "severityCounts": report["severityCounts"],
        "highestSeverityScenario": report["highestSeverityScenario"],
        "operatingPrinciples": report["operatingPrinciples"],
        "scenarios": report["scenarios"],
    }
    output = "export const incidentResponse = " + json.dumps(lab, indent=2, ensure_ascii=False) + ";\n"
    Path(path).write_text(output, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate incident response tabletop artifacts.")
    parser.add_argument("--scenarios", default="incident_response/incident_scenarios.json")
    parser.add_argument("--out", default="audit_outputs/incident_response_tabletop.json")
    parser.add_argument("--markdown-out", default="audit_outputs/incident_response_tabletop.md")
    parser.add_argument("--lab-summary", default="crypto-scam-lab/data/incidentResponse.js")
    args = parser.parse_args()

    scenarios = load_scenarios(args.scenarios)
    report = generate_report(scenarios)

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    Path(args.markdown_out).write_text(render_markdown(report), encoding="utf-8")
    write_lab_summary(report, args.lab_summary)
    print(json.dumps({"scenarioCount": report["scenarioCount"], "severityCounts": report["severityCounts"]}, indent=2))


if __name__ == "__main__":
    main()
