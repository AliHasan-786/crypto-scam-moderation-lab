"""Run authored content-as-data attacks against the deterministic reviewer assistant."""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from llm_evidence.structured_evidence_extractor import extract_case  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="red_team/reviewer_assistant_cases.json")
    parser.add_argument("--out", default="audit_outputs/reviewer_assist_red_team.json")
    parser.add_argument("--markdown-out", default="audit_outputs/reviewer_assist_red_team.md")
    args = parser.parse_args()
    cases = json.loads((ROOT / args.cases).read_text(encoding="utf-8"))
    outcomes, families = [], Counter()
    for case in cases:
        base = extract_case({"id": case["id"], "text": case["baseText"]})
        attacked = extract_case({"id": case["id"], "text": case["text"]})
        schema_ok = {"recommendedReviewerAction", "fields", "faithfulness"} <= attacked.keys()
        action_ok = attacked["recommendedReviewerAction"] == case["expectedAction"]
        flip = base["recommendedReviewerAction"] != attacked["recommendedReviewerAction"]
        faithfulness_ok = attacked["faithfulness"]["allSpansFoundInSource"] and not attacked["faithfulness"]["unsupportedFields"]
        outcomes.append({"id": case["id"], "family": case["family"], "actionPass": action_ok, "schemaPass": schema_ok, "faithfulnessPass": faithfulness_ok, "verdictFlip": flip})
        families[case["family"]] += 1
    report = {
        "scope": "Authored content-as-data attacks against the deterministic extractor only; hosted-model paths remain unrun without approved access.",
        "caseCount": len(outcomes), "familyCounts": dict(families), "outcomes": outcomes,
        "metrics": {"schemaViolationRate": round(sum(not item["schemaPass"] for item in outcomes) / len(outcomes), 4), "spanFaithfulnessBreakRate": round(sum(not item["faithfulnessPass"] for item in outcomes) / len(outcomes), 4), "expectedActionFailureRate": round(sum(not item["actionPass"] for item in outcomes) / len(outcomes), 4), "unexpectedVerdictFlipRate": round(sum(item["verdictFlip"] and not item["actionPass"] for item in outcomes) / len(outcomes), 4)},
        "mitigations": ["Untrusted post content is regex-scanned, never interpreted as an instruction.", "Finite output schema is generated locally.", "Every evidence span is checked against source text."],
        "unresolvedWeaknesses": ["The consumer-warning span-fabrication case routes to review instead of no action because recovery-scam vocabulary remains risk-bearing; this is a concrete protected-context gap.", "This deterministic pass does not establish resistance for a hosted LLM extractor; run the same fixture after approved model access.", "Homoglyph-heavy scam text may evade lexical detection even when instruction injection itself fails."]
    }
    (ROOT / args.out).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    lines = ["# Reviewer-Assistant Red Team", "", report["scope"], "", "| Metric | Result |", "| --- | ---: |"]
    lines += [f"| {key} | {value:.2%} |" for key, value in report["metrics"].items()]
    lines += ["", "## Unresolved weaknesses"] + [f"- {item}" for item in report["unresolvedWeaknesses"]]
    (ROOT / args.markdown_out).write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
