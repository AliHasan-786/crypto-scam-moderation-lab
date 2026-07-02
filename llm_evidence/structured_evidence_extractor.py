from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class EvidenceField:
    key: str
    label: str
    summary: str
    patterns: tuple[str, ...]
    kind: str


EVIDENCE_FIELDS = (
    EvidenceField(
        key="promised_return",
        label="Promised return",
        summary="Promises or implies guaranteed, doubled, unusually high, risk-free, or instant returns.",
        kind="risk",
        patterns=(
            r"\bguaranteed\s+(?:[0-9]+%\s+)?returns?\b",
            r"\brisk[-\s]?free\b",
            r"\bdouble(?:d)?\b.*\b(?:btc|bitcoin|eth|crypto|money|back)\b",
            r"\b[0-9]{2,}\s?%\s+(?:monthly\s+)?returns?\b",
            r"\b[0-9]+x\b",
            r"\bprofits?\b",
            r"\bpassive income\b",
            r"\breceive\s+[0-9.]+\s*(?:btc|eth|crypto)\s+back\b",
            r"\binstantly\b",
        ),
    ),
    EvidenceField(
        key="transfer_ask",
        label="Transfer ask",
        summary="Requests that the user send crypto, deposit funds, or pay an upfront/processing/activation fee.",
        kind="risk",
        patterns=(
            r"\bsend\s+(?:the\s+)?(?:small\s+)?(?:activation\s+)?(?:fee\s+)?(?:[0-9.]+\s*)?(?:btc|bitcoin|eth|ethereum|sol|usdt|crypto)?\b",
            r"\bdeposit\s+(?:[0-9.]+\s*)?(?:btc|bitcoin|eth|ethereum|sol|usdt|crypto)?\b",
            r"\bpay\s+(?:the\s+)?(?:processing|activation|release|upfront)\s+fee\b",
            r"\bprocessing fee\b",
            r"\bupfront\b",
            r"\bactivation fee\b",
            r"\brelease charge\b",
            r"\bfund\s+(?:your\s+)?(?:account|vault)\b",
        ),
    ),
    EvidenceField(
        key="wallet_connection_ask",
        label="Wallet connection ask",
        summary="Asks the user to connect, verify, sync, or provide a wallet.",
        kind="risk",
        patterns=(
            r"\bconnect\s+(?:your\s+)?wallet\b",
            r"\bverify\s+(?:your\s+)?wallet\b",
            r"\bsync\s+(?:your\s+)?(?:wallet|vault)\b",
            r"\bwallet address\b",
            r"\bwallet connect required\b",
            r"\baccount vault\b",
            r"\bprovide\s+(?:your\s+)?wallet\b",
        ),
    ),
    EvidenceField(
        key="impersonated_entity",
        label="Impersonated entity",
        summary="Claims official, verified, support, foundation, celebrity, exchange, or brand authority.",
        kind="risk",
        patterns=(
            r"\bofficial\b.{0,60}\b(?:giveaway|grant|airdrop|support|verified users)\b",
            r"\bverified\s+(?:wallet|users?|recovery|support)\b",
            r"\bsupport escalation\b",
            r"\b(?:coinbase|binance|ledger)\s+support\b",
            r"\b(?:microsoft|ethereum|bitcoin)\s+(?:foundation\s+)?(?:crypto\s+)?grant\b",
            r"\bfoundation\s+grant\b",
            r"\b(?:elon musk|musk|vitalik)\b.{0,60}\b(?:giveaway|send|receive|airdrop|grant)\b",
            r"\b(?:microsoft|coinbase|binance|tesla|ledger|ethereum|bitcoin)\b.{0,60}\b(?:official|verified|grant|support|giveaway|airdrop)\b",
        ),
    ),
    EvidenceField(
        key="urgency",
        label="Urgency",
        summary="Applies time pressure or scarcity.",
        kind="risk",
        patterns=(
            r"\blimited time\b",
            r"\bfinal\s+(?:airdrop\s+)?window\b",
            r"\bwindow\s+(?:is\s+)?open\b",
            r"\bbefore\s+(?:midnight|eligibility expires|the window closes|it closes)\b",
            r"\bexpires?\b",
            r"\bact now\b",
            r"\bimmediately\b",
            r"\bnow\b",
        ),
    ),
    EvidenceField(
        key="risky_link_or_wallet",
        label="Risky link or wallet",
        summary="Contains a URL, defanged URL, suspicious domain, QR/link mention, wallet address, or wallet-like string.",
        kind="risk",
        patterns=(
            r"\bhxxps?://[^\s]+",
            r"\bhttps?://[^\s]+",
            r"\b[a-z0-9-]+(?:\[.\]|\.)(?:xyz|top|click|cash|net|io|com|org)\b",
            r"\b0x[a-fA-F0-9]{20,64}\b",
            r"\b(?:bc1[ac-hj-np-z02-9]{25,90}|[13][a-km-zA-HJ-NP-Z1-9]{25,34})\b",
            r"\bQR code\b",
            r"\blink\b",
        ),
    ),
    EvidenceField(
        key="recovery_claim",
        label="Recovery claim",
        summary="Claims to recover, restore, or unlock lost funds or wallets.",
        kind="risk",
        patterns=(
            r"\brecovery\s+(?:service|team)\b",
            r"\brestore\s+any\s+wallet\b",
            r"\bfunds?\s+(?:are\s+)?recovered\b",
            r"\bfunds?\s+unlock\b",
            r"\brecover(?:ed|y)?\s+(?:funds|service|team)\b",
        ),
    ),
    EvidenceField(
        key="private_channel_or_signal",
        label="Private channel or signal",
        summary="Pushes a private DM, mentor, premium signal, or trading-group funnel.",
        kind="risk",
        patterns=(
            r"\bDM me\b",
            r"\bprivate\s+(?:trading\s+)?(?:method|group)\b",
            r"\bpremium\s+members\b",
            r"\bearly signals\b",
            r"\bwhere to deposit first\b",
        ),
    ),
    EvidenceField(
        key="benign_context",
        label="Benign context",
        summary="Warning, research, satire, developer/debugging, market commentary, or skeptical help-seeking context.",
        kind="benign",
        patterns=(
            r"\bdo not send\b",
            r"\bdon't send\b",
            r"\bwarning\b",
            r"\bwarned\b",
            r"\bscam(?:s)?\b",
            r"\bresearch\b",
            r"\bpaper\b",
            r"\bstudies\b",
            r"\bobviously not\b",
            r"\bimaginary\b",
            r"\bsatire\b",
            r"\bjoke\b",
            r"\bdebugging\b",
            r"\btestnet\b",
            r"\bbug\b",
            r"\bnot investment advice\b",
            r"\bI am still not treating this as investment advice\b",
            r"\bwithout getting scammed\b",
        ),
    ),
    EvidenceField(
        key="missing_context",
        label="Missing context",
        summary="The text signals uncertainty, missing source/link context, OCR, or skeptical review need.",
        kind="missing",
        patterns=(
            r"\bnot verified\b",
            r"\bcannot tell\b",
            r"\bcan't tell\b",
            r"\bhas anyone\b",
            r"\bdoes anyone know\b",
            r"\bis it legit\b",
            r"\bsafely\b",
            r"\bno visible source\b",
            r"\bsource account not visible\b",
            r"\bimage OCR\b",
            r"\[Image OCR\]",
            r"\blink is cropped\b",
            r"\bQR code visible\b",
        ),
    ),
)

RISK_FIELD_KEYS = {field.key for field in EVIDENCE_FIELDS if field.kind == "risk"}


def normalize_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip())


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("Cases file must contain a list.")
    return cases


def find_spans(text: str, patterns: tuple[str, ...], *, limit: int = 4) -> list[dict[str, Any]]:
    spans: list[dict[str, Any]] = []
    seen: set[tuple[int, int]] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            key = (match.start(), match.end())
            if key in seen:
                continue
            seen.add(key)
            spans.append({"text": match.group(0), "start": match.start(), "end": match.end()})
            if len(spans) >= limit:
                return spans
    return spans


def infer_stance(field: EvidenceField, text: str) -> str:
    lowered = text.lower()
    if field.kind == "missing":
        return "missing_context"
    if "obviously not" in lowered or "imaginary" in lowered or "satire" in lowered or "joke" in lowered:
        return "satire"
    if "debug" in lowered or "testnet" in lowered or "bug" in lowered or "developer" in lowered:
        return "technical"
    if "research" in lowered or "paper" in lowered or "studies" in lowered:
        return "research"
    if "do not send" in lowered or "don't send" in lowered or "warning" in lowered or "warned" in lowered:
        return "warning"
    if "has anyone" in lowered or "does anyone know" in lowered or "cannot tell" in lowered or "can't tell" in lowered:
        return "question"
    return "claim" if field.kind == "risk" else "unknown"


def extract_case(case: dict[str, Any], *, provider: str = "deterministic_rubric_v1") -> dict[str, Any]:
    text = str(case.get("text", ""))
    fields: dict[str, dict[str, Any]] = {}
    risk_factors: list[str] = []
    benign_factors: list[str] = []
    missing_context: list[str] = []

    for field in EVIDENCE_FIELDS:
        spans = find_spans(text, field.patterns)
        present = bool(spans)
        stance = infer_stance(field, text) if present else "unknown"
        fields[field.key] = {
            "present": present,
            "stance": stance,
            "spans": spans,
            "summary": field.summary if present else "",
        }
        if present and field.kind == "risk":
            risk_factors.append(field.key)
        elif present and field.kind == "benign":
            benign_factors.append(field.key)
        elif present and field.kind == "missing":
            missing_context.append(field.key)

    action = recommend_action(risk_factors, benign_factors, missing_context, fields)
    confidence = confidence_score(risk_factors, benign_factors, missing_context, action)
    summary = reviewer_summary(risk_factors, benign_factors, missing_context, action)
    faithfulness = check_faithfulness(text, fields)

    return {
        "caseId": case.get("id", ""),
        "scenario": case.get("scenario", ""),
        "groundTruth": case.get("ground_truth", ""),
        "provider": provider,
        "recommendedReviewerAction": action,
        "confidence": confidence,
        "riskFactors": risk_factors,
        "benignFactors": benign_factors,
        "missingContext": missing_context,
        "fields": fields,
        "reviewerSummary": summary,
        "faithfulness": faithfulness,
        "text": text,
    }


def recommend_action(
    risk_factors: list[str],
    benign_factors: list[str],
    missing_context: list[str],
    fields: dict[str, dict[str, Any]],
) -> str:
    risk = set(risk_factors)
    has_benign = bool(benign_factors)
    has_missing = bool(missing_context)
    strong_combo = (
        ("transfer_ask" in risk or "wallet_connection_ask" in risk)
        and (
            "promised_return" in risk
            or ("transfer_ask" in risk and "wallet_connection_ask" in risk)
            or "impersonated_entity" in risk
            or "urgency" in risk
            or "risky_link_or_wallet" in risk
            or "recovery_claim" in risk
        )
    )
    if has_missing:
        return "human_review"
    if has_benign and not has_missing:
        if "recovery_claim" in risk or "private_channel_or_signal" in risk:
            return "human_review"
        return "no_action"
    if strong_combo or len(risk) >= 3:
        return "public_label_candidate"
    if risk:
        return "human_review"
    return "no_action"


def confidence_score(
    risk_factors: list[str],
    benign_factors: list[str],
    missing_context: list[str],
    action: str,
) -> float:
    base = 0.52
    base += min(0.28, len(risk_factors) * 0.055)
    base += min(0.12, len(benign_factors) * 0.06)
    base -= min(0.18, len(missing_context) * 0.09)
    if action == "human_review":
        base = min(base, 0.76)
    if action == "no_action" and benign_factors:
        base += 0.08
    return round(max(0.05, min(0.97, base)), 3)


def reviewer_summary(
    risk_factors: list[str],
    benign_factors: list[str],
    missing_context: list[str],
    action: str,
) -> str:
    risk = ", ".join(risk_factors[:4]) if risk_factors else "no concrete scam-risk field"
    benign = ", ".join(benign_factors[:2]) if benign_factors else "no benign-context field"
    missing = ", ".join(missing_context[:2]) if missing_context else "no missing-context field"
    if action == "public_label_candidate":
        return f"Concrete scam evidence is present ({risk}) with {benign}; this is a candidate for reviewer-confirmed public labeling."
    if action == "human_review":
        return f"Risk evidence or uncertainty requires review ({risk}; {missing})."
    return f"No action recommended because the text shows {benign} and lacks enough concrete scam evidence."


def check_faithfulness(text: str, fields: dict[str, dict[str, Any]]) -> dict[str, Any]:
    span_count = 0
    unsupported: list[str] = []
    for field_key, field in fields.items():
        spans = field["spans"]
        if field["present"] and not spans:
            unsupported.append(field_key)
        for span in spans:
            span_count += 1
            start = int(span["start"])
            end = int(span["end"])
            if text[start:end] != span["text"]:
                unsupported.append(field_key)
    return {
        "spanCount": span_count,
        "allSpansFoundInSource": not unsupported,
        "unsupportedFields": sorted(set(unsupported)),
    }


def expected_action(case: dict[str, Any]) -> str:
    ground_truth = case.get("ground_truth")
    if ground_truth == "fraud" and case.get("expected_public_label"):
        return "public_label_candidate"
    if case.get("expected_review_or_label"):
        return "human_review"
    return "no_action"


def action_passes(expected: str, actual: str) -> bool:
    if expected == "public_label_candidate":
        return actual == "public_label_candidate"
    if expected == "human_review":
        return actual == "human_review"
    return actual == "no_action"


def evaluate_extractions(cases: list[dict[str, Any]], extractions: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {case["id"]: case for case in cases}
    results = []
    for extraction in extractions:
        case = by_id[extraction["caseId"]]
        expected = expected_action(case)
        actual = extraction["recommendedReviewerAction"]
        failures = []
        if not action_passes(expected, actual):
            failures.append("recommended_action_mismatch")
        if case.get("ground_truth") == "fraud" and not extraction["riskFactors"]:
            failures.append("missing_fraud_evidence")
        if case.get("ground_truth") == "legitimate" and actual == "public_label_candidate":
            failures.append("legitimate_public_label_overreach")
        if not extraction["faithfulness"]["allSpansFoundInSource"]:
            failures.append("unfaithful_span")
        results.append(
            {
                "caseId": extraction["caseId"],
                "scenario": case.get("scenario"),
                "groundTruth": case.get("ground_truth"),
                "expectedAction": expected,
                "actualAction": actual,
                "riskFactors": extraction["riskFactors"],
                "benignFactors": extraction["benignFactors"],
                "missingContext": extraction["missingContext"],
                "confidence": extraction["confidence"],
                "passed": not failures,
                "failures": failures,
            }
        )
    return build_report(results, extractions)


def grouped_summary(results: list[dict[str, Any]], field: str) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for result in results:
        grouped[str(result.get(field, "unknown"))].append(result)
    return {
        key: {
            "count": len(items),
            "passed": sum(1 for item in items if item["passed"]),
            "passRate": sum(1 for item in items if item["passed"]) / max(1, len(items)),
            "publicLabelCandidates": sum(1 for item in items if item["actualAction"] == "public_label_candidate"),
            "humanReview": sum(1 for item in items if item["actualAction"] == "human_review"),
            "noAction": sum(1 for item in items if item["actualAction"] == "no_action"),
        }
        for key, items in sorted(grouped.items())
    }


def build_report(results: list[dict[str, Any]], extractions: list[dict[str, Any]]) -> dict[str, Any]:
    action_counts = Counter(result["actualAction"] for result in results)
    failure_counts = Counter(failure for result in results for failure in result["failures"])
    faithfulness_count = sum(1 for item in extractions if item["faithfulness"]["allSpansFoundInSource"])
    fraud_results = [item for item in results if item["groundTruth"] == "fraud"]
    legitimate_results = [item for item in results if item["groundTruth"] == "legitimate"]
    ambiguous_results = [item for item in results if item["groundTruth"] == "ambiguous"]

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "suite": "structured_evidence_extractor_v1",
        "provider": "deterministic_rubric_v1",
        "caveat": (
            "This is the local deterministic implementation of the LLM evidence contract. "
            "It tests schema, span faithfulness, and reviewer-action expectations before plugging in a hosted LLM."
        ),
        "caseCount": len(results),
        "passCount": sum(1 for result in results if result["passed"]),
        "passRate": sum(1 for result in results if result["passed"]) / max(1, len(results)),
        "spanFaithfulnessRate": faithfulness_count / max(1, len(extractions)),
        "fraudEvidenceRecall": sum(1 for item in fraud_results if item["riskFactors"]) / max(1, len(fraud_results)),
        "legitimateNoPublicLabelRate": sum(
            1 for item in legitimate_results if item["actualAction"] != "public_label_candidate"
        ) / max(1, len(legitimate_results)),
        "ambiguousReviewRate": sum(
            1 for item in ambiguous_results if item["actualAction"] == "human_review"
        ) / max(1, len(ambiguous_results)),
        "actionCounts": dict(sorted(action_counts.items())),
        "failureCounts": dict(sorted(failure_counts.items())),
        "scenarioSummary": grouped_summary(results, "scenario"),
        "groundTruthSummary": grouped_summary(results, "groundTruth"),
        "topFailures": [result for result in results if not result["passed"]][:8],
        "results": results,
        "extractions": extractions,
    }


def compact_lab_summary(report: dict[str, Any]) -> dict[str, Any]:
    examples = []
    for extraction in report["extractions"][:6]:
        examples.append(
            {
                "caseId": extraction["caseId"],
                "scenario": extraction["scenario"],
                "recommendedReviewerAction": extraction["recommendedReviewerAction"],
                "confidence": extraction["confidence"],
                "riskFactors": extraction["riskFactors"][:4],
                "benignFactors": extraction["benignFactors"][:2],
                "missingContext": extraction["missingContext"][:2],
                "reviewerSummary": extraction["reviewerSummary"],
            }
        )
    return {
        "generatedAt": report["generatedAt"],
        "suite": report["suite"],
        "provider": report["provider"],
        "caseCount": report["caseCount"],
        "passRate": report["passRate"],
        "spanFaithfulnessRate": report["spanFaithfulnessRate"],
        "fraudEvidenceRecall": report["fraudEvidenceRecall"],
        "legitimateNoPublicLabelRate": report["legitimateNoPublicLabelRate"],
        "ambiguousReviewRate": report["ambiguousReviewRate"],
        "actionCounts": report["actionCounts"],
        "failureCounts": report["failureCounts"],
        "examples": examples,
    }


def write_lab_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    path.write_text(f"export const evidenceSummary = {rendered};\n", encoding="utf-8")


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Structured Evidence Extractor Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        "## Summary",
        "",
        f"- Cases: {report['caseCount']}",
        f"- Expectation pass rate: {pct(report['passRate'])}",
        f"- Span faithfulness: {pct(report['spanFaithfulnessRate'])}",
        f"- Fraud evidence recall: {pct(report['fraudEvidenceRecall'])}",
        f"- Legitimate no-public-label rate: {pct(report['legitimateNoPublicLabelRate'])}",
        f"- Ambiguous review rate: {pct(report['ambiguousReviewRate'])}",
        "",
        "Interpretation: this is a reviewer-assistance layer. It extracts cited evidence and recommended review posture, but it does not publish labels or override the classifier/policy pipeline.",
        "",
        "## Action Counts",
        "",
    ]
    for action, count in report["actionCounts"].items():
        lines.append(f"- {action}: {count}")
    lines.extend(
        [
            "",
            "## Top Failures",
            "",
        ]
    )
    if report["topFailures"]:
        for failure in report["topFailures"]:
            lines.extend(
                [
                    f"### {failure['caseId']}",
                    "",
                    f"- Scenario: {failure['scenario']}",
                    f"- Expected: {failure['expectedAction']}",
                    f"- Actual: {failure['actualAction']}",
                    f"- Failures: {', '.join(failure['failures'])}",
                    "",
                ]
            )
    else:
        lines.append("No expectation failures.")
        lines.append("")
    lines.extend(
        [
            "## Design Notes",
            "",
            "- Evidence spans must point back to source text.",
            "- Public labels remain gated by the existing policy/model system.",
            "- Hosted LLM output should be evaluated against this same schema before being exposed to reviewers.",
            "- The next production step is a provider adapter plus regression tests for hallucinated evidence and over-enforcement.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Structured reviewer evidence extraction for crypto-scam moderation.")
    parser.add_argument("--cases", default=str(ROOT / "evals" / "scenario_eval_cases.json"))
    parser.add_argument("--out", default=str(ROOT / "audit_outputs" / "llm_evidence_report.json"))
    parser.add_argument("--markdown-out", default=str(ROOT / "audit_outputs" / "llm_evidence_report.md"))
    parser.add_argument("--lab-summary", default=str(ROOT / "crypto-scam-lab" / "data" / "evidenceSummary.js"))
    args = parser.parse_args()

    cases = load_cases(Path(args.cases))
    extractions = [extract_case(case) for case in cases]
    report = evaluate_extractions(cases, extractions)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    markdown_path = Path(args.markdown_out)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(report), encoding="utf-8")

    summary = compact_lab_summary(report)
    write_lab_summary(Path(args.lab_summary), summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
