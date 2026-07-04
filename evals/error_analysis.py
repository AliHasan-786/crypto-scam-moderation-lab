"""Standing error-analysis surface.

Publishes the system's real failures instead of hiding them behind green gates:

1. Decision-level false positives on the held-out test set (legitimate posts
   that would become public-label candidates or escalations), categorized.
2. Decision-level misses (fraud that gets no action at all).
3. Authored "unsolved" hard cases the system is NOT expected to handle yet.
   Failures here are published, not fixed-then-hidden. When one starts
   passing, it is promoted to the scenario suite and replaced with something
   harder (see policy/DECISION_LOG.md, entry 010).

The release gate intentionally does NOT require unsolved cases to pass —
only the guard cases (protected contexts that must never regress).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import policy_proposal_labeler_v2 as v2  # noqa: E402

LABELING_ACTIONS = {"apply_potential_crypto_fraud_label", "high_confidence_escalation"}

DOUBT_MARKERS = (
    r"haven'?t verified",
    r"can'?t find",
    r"not sure",
    r"no regulatory",
    r"hard to tell",
    r"is (?:this|it) (?:legit|a scam)",
    r"anyone (?:else )?(?:tried|tested|looked)",
    r"waiting for more",
)

REPORTAGE_MARKERS = (
    r"^\W*(?:i saw|someone|a friend|a platform|a trading platform|a crypto|an ad|they)",
    r"dm'?d me",
    r"shared a link",
    r"i keep hearing",
    r"i'?ve been seeing",
)

FP_CATEGORY_COMMENTARY = {
    "skeptical_third_party_report": (
        "The poster is describing an offer and signalling doubt — reporting, not "
        "promoting. The classifier keys on the described scam's features; the "
        "uncertain-review context patterns do not cover first-person reportage. "
        "This is the system's largest real false-positive class, and the reason "
        "reviewer confirmation is mandatory before any label (Decision Log 003/004). "
        "Candidate fix: a speaker-stance feature (describing vs. soliciting); risk: "
        "scammers adopting doubt language as camouflage — see unsolved-002."
    ),
    "personal_solicitation_out_of_scope": (
        "Begging for crypto is not an investment scam under this policy (no promised "
        "return, no fake opportunity). Wrong under this policy's definition even if "
        "another policy might cover spam or solicitation. Candidate fix: require a "
        "return-promise or opportunity claim before transfer-request evidence counts "
        "toward labeling."
    ),
    "naive_question": (
        "A short curiosity question tripping free-crypto patterns. Labeling a "
        "question as fraud is a category error; at most this deserves a safety "
        "resource surface. Candidate fix: interrogative-form dampening."
    ),
    "uncategorized": (
        "Does not fit a known false-positive class yet. Uncategorized FPs are the "
        "queue for discovering the next pattern."
    ),
}


def categorize_fp(text: str) -> str:
    lower = text.lower().strip().strip('"“”')
    doubt = any(re.search(p, lower) for p in DOUBT_MARKERS)
    reportage = any(re.search(p, lower) for p in REPORTAGE_MARKERS)
    if doubt and reportage:
        return "skeptical_third_party_report"
    if doubt or reportage:
        return "skeptical_third_party_report"
    if re.search(r"(please )?send (?:me )?some", lower) and not re.search(
        r"double|return|profit|guarantee", lower
    ):
        return "personal_solicitation_out_of_scope"
    if lower.endswith("?") and len(lower) < 80:
        return "naive_question"
    return "uncategorized"


def load_test_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def analyze(args: argparse.Namespace) -> dict:
    artifact = joblib.load(args.model_path)
    pipeline = artifact["model"]
    thresholds = artifact["thresholds"]

    rows = load_test_rows(Path(args.test))
    texts = [row["Post Content"] for row in rows]
    labels = [int(row["Ground Truth Label"]) for row in rows]
    probabilities = pipeline.predict_proba(texts)[:, 1]

    false_positives = []
    misses = []
    downgrades = []
    for index, (text, label, probability) in enumerate(
        zip(texts, labels, probabilities)
    ):
        action = v2.decision_for_text(text, float(probability), thresholds)
        if label == 0 and action in LABELING_ACTIONS:
            category = categorize_fp(text)
            false_positives.append(
                {
                    "caseId": f"test-fp-{index:03d}",
                    "text": text,
                    "score": round(float(probability), 4),
                    "action": action,
                    "category": category,
                    "commentary": FP_CATEGORY_COMMENTARY[category],
                }
            )
        elif label == 1 and action == "no_label":
            misses.append(
                {
                    "caseId": f"test-miss-{index:03d}",
                    "text": text,
                    "score": round(float(probability), 4),
                }
            )
        elif label == 1 and action == "send_to_human_review":
            downgrades.append(
                {
                    "caseId": f"test-review-{index:03d}",
                    "score": round(float(probability), 4),
                }
            )

    unsolved_payload = json.loads(Path(args.unsolved).read_text(encoding="utf-8"))
    unsolved_results = []
    guard_failures = 0
    for case in unsolved_payload["cases"]:
        probability = float(pipeline.predict_proba([case["text"]])[0, 1])
        action = v2.decision_for_text(case["text"], probability, thresholds)
        # An escalation satisfies an expected label (strictly stronger action);
        # exceeding an expected *review* is overreach and stays a failure.
        matches = action == case["expected_action"] or (
            case["expected_action"] == "apply_potential_crypto_fraud_label"
            and action == "high_confidence_escalation"
        )
        is_guard = case["id"].startswith("guard-")
        if is_guard and not matches:
            guard_failures += 1
        unsolved_results.append(
            {
                "id": case["id"],
                "category": case["category"],
                "text": case["text"],
                "expectedAction": case["expected_action"],
                "actualAction": action,
                "score": round(probability, 4),
                "status": "pass" if matches else ("GUARD FAILURE" if is_guard else "known failure"),
                "rationale": case["rationale"],
                "knownBlindSpot": case.get("known_blind_spot"),
            }
        )

    open_failures = [r for r in unsolved_results if r["status"] == "known failure"]
    fp_categories: dict[str, int] = {}
    for item in false_positives:
        fp_categories[item["category"]] = fp_categories.get(item["category"], 0) + 1

    return {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "testRows": len(rows),
        "thresholds": {k: round(float(t), 4) for k, t in thresholds.items()},
        "decisionLevelFalsePositives": false_positives,
        "falsePositiveCategories": fp_categories,
        "decisionLevelMisses": misses,
        "reviewDowngradeCount": len(downgrades),
        "unsolvedCases": unsolved_results,
        "openFailureCount": len(open_failures),
        "guardFailureCount": guard_failures,
        "summary": {
            "falsePositiveCount": len(false_positives),
            "missCount": len(misses),
            "unsolvedTotal": len([r for r in unsolved_results if not r["id"].startswith("guard-")]),
            "unsolvedStillFailing": len(open_failures),
            "guardsPassing": guard_failures == 0,
        },
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# Error Analysis — What This System Gets Wrong",
        "",
        f"Generated {report['generatedAt']}. "
        f"{report['summary']['falsePositiveCount']} decision-level false positives, "
        f"{report['summary']['missCount']} full misses on the held-out test set; "
        f"{report['summary']['unsolvedStillFailing']} of "
        f"{report['summary']['unsolvedTotal']} authored hard cases still failing "
        "(published deliberately — see Decision Log 010).",
        "",
        "## Decision-level false positives (held-out test set)",
        "",
        "Legitimate posts that would reach label-candidate or escalation before a "
        "reviewer touches them. Reviewer confirmation is the control that keeps "
        "these from becoming user-visible harm.",
        "",
    ]
    for item in report["decisionLevelFalsePositives"]:
        lines += [
            f"### {item['caseId']} — {item['category']} (score {item['score']:.2f}, {item['action']})",
            "",
            f"> {item['text']}",
            "",
            item["commentary"],
            "",
        ]
    lines += ["## Full misses (fraud receiving no action)", ""]
    if not report["decisionLevelMisses"]:
        lines.append(
            "None at the current operating point (recall 1.0 on this corpus — a fact "
            "that says as much about corpus size as about the model)."
        )
    else:
        for item in report["decisionLevelMisses"]:
            lines.append(f"- {item['caseId']} (score {item['score']:.2f}): {item['text'][:140]}")
    lines += [
        "",
        "## Unsolved hard cases (standing red-team surface)",
        "",
        "| Case | Category | Expected | Actual | Status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for result in report["unsolvedCases"]:
        lines.append(
            f"| {result['id']} | {result['category']} | {result['expectedAction']} "
            f"| {result['actualAction']} | {result['status']} |"
        )
    lines += ["", "### Why each failure is still open", ""]
    for result in report["unsolvedCases"]:
        if result["status"] == "known failure":
            lines += [
                f"**{result['id']} ({result['category']}):** {result['rationale']}"
                + (
                    f" _Blind spot: {result['knownBlindSpot']}_"
                    if result.get("knownBlindSpot")
                    else ""
                ),
                "",
            ]
    return "\n".join(lines) + "\n"


def to_lab_summary(report: dict) -> str:
    payload = {
        "generatedAt": report["generatedAt"],
        "thresholds": report["thresholds"],
        "falsePositives": report["decisionLevelFalsePositives"],
        "falsePositiveCategories": report["falsePositiveCategories"],
        "missCount": report["summary"]["missCount"],
        "unsolvedCases": report["unsolvedCases"],
        "summary": report["summary"],
        "categoryCommentary": FP_CATEGORY_COMMENTARY,
    }
    return (
        "export const errorAnalysis = "
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + ";\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--test", default="test.csv")
    parser.add_argument("--model-path", default="audit_outputs/fraud_labeler_v2.joblib")
    parser.add_argument("--unsolved", default="evals/unsolved_cases.json")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown-out")
    parser.add_argument("--lab-summary")
    args = parser.parse_args()

    report = analyze(args)
    Path(args.out).write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    if args.markdown_out:
        Path(args.markdown_out).write_text(to_markdown(report), encoding="utf-8")
    if args.lab_summary:
        Path(args.lab_summary).write_text(to_lab_summary(report), encoding="utf-8")

    print(
        json.dumps(
            {
                "falsePositives": report["summary"]["falsePositiveCount"],
                "misses": report["summary"]["missCount"],
                "unsolvedStillFailing": report["summary"]["unsolvedStillFailing"],
                "guardsPassing": report["summary"]["guardsPassing"],
            },
            indent=2,
        )
    )
    # Guard cases are enforceable; unsolved failures are not.
    return 0 if report["guardFailureCount"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
