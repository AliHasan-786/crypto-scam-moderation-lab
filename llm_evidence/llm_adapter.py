"""Hosted-LLM evidence adapter with a cached mode for the static public demo.

Three providers:

- ``cached`` (default): loads pre-generated LLM outputs from
  ``llm_evidence/cache/llm_evidence_cache.json``. The public demo stays
  static, free, and key-less (Decision Log 009). Cache provenance (model,
  date) is surfaced in every report.
- ``anthropic`` / ``openai``: regenerate live against a hosted model using
  the same system prompt as the deterministic extractor
  (``llm_evidence/prompts/evidence_extractor_system.md``). Requires
  ``ANTHROPIC_API_KEY`` or ``OPENAI_API_KEY``.

Regardless of provider, outputs pass through the SAME span-faithfulness
check as the deterministic extractor (`check_faithfulness` is imported from
it, not reimplemented) — generated evidence is only trusted when every claim
is backed by a verbatim source span.

The adapter also produces a baseline-vs-LLM comparison: agreement per case,
expectation pass rates side by side, and an honest cost/latency table. The
point is not that the LLM wins — it is to show WHERE each approach earns its
cost (see the stance-detection discussion in the comparison report).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import joblib

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import policy_proposal_labeler_v2 as v2  # noqa: E402
from llm_evidence.structured_evidence_extractor import (  # noqa: E402
    check_faithfulness,
    expected_action,
    action_passes,
)

FIELD_KEYS = (
    "promised_return",
    "transfer_ask",
    "wallet_connection_ask",
    "impersonated_entity",
    "urgency",
    "risky_link_or_wallet",
    "recovery_claim",
    "private_channel_or_signal",
    "benign_context",
    "missing_context",
)

BASELINE_TO_REVIEWER_ACTION = {
    "high_confidence_escalation": "public_label_candidate",
    "apply_potential_crypto_fraud_label": "public_label_candidate",
    "send_to_human_review": "human_review",
    "no_label": "no_action",
}

# Honest, order-of-magnitude economics for the comparison table. Baseline
# inference is effectively free; LLM calls are not. Assumes ~700 input +
# ~450 output tokens per case at mid-tier hosted-model prices (2026).
COST_MODEL = {
    "baselinePer1kPosts": "$0 (CPU, <1 ms/post)",
    "llmPer1kPosts": "$5-15 depending on model tier (700 in / 450 out tokens/post)",
    "llmLatencyPerPost": "1-4 s per call vs <1 ms baseline",
    "operationalNote": (
        "At 1M posts/day the LLM cannot be the first-pass filter on cost alone. "
        "The defensible architecture is baseline-first triage with LLM evidence "
        "extraction only on the review-queue slice (~5-20% of volume), which is "
        "exactly how this lab wires it."
    ),
}


def default_fields() -> dict:
    return {
        key: {"present": False, "stance": "unknown", "spans": [], "summary": ""}
        for key in FIELD_KEYS
    }


def resolve_spans(case_text: str, span_texts: list[str]) -> list[dict]:
    spans = []
    for span_text in span_texts:
        start = case_text.find(span_text)
        if start < 0:
            # Deliberately record an unresolvable span: the faithfulness
            # check must see and fail it rather than have it silently dropped.
            spans.append({"text": span_text, "start": 0, "end": 0})
            continue
        spans.append({"text": span_text, "start": start, "end": start + len(span_text)})
    return spans


def extraction_from_cache(case: dict, cached: dict, provider_label: str) -> dict:
    fields = default_fields()
    for key, field in cached.get("fields", {}).items():
        fields[key] = {
            "present": bool(field.get("present")),
            "stance": field.get("stance", "unknown"),
            "spans": resolve_spans(case["text"], field.get("spanTexts", [])),
            "summary": field.get("summary", ""),
        }
    extraction = {
        "caseId": case["id"],
        "provider": provider_label,
        "recommendedReviewerAction": cached["recommendedReviewerAction"],
        "confidence": cached["confidence"],
        "riskFactors": cached.get("riskFactors", []),
        "benignFactors": cached.get("benignFactors", []),
        "missingContext": cached.get("missingContext", []),
        "fields": fields,
        "reviewerSummary": cached.get("reviewerSummary", ""),
    }
    extraction["faithfulness"] = check_faithfulness(case["text"], fields)
    return extraction


def call_hosted_model(provider: str, system_prompt: str, case: dict) -> dict:
    """Minimal dependency-free HTTPS call for live regeneration."""
    user_prompt = (
        "Extract evidence for this case and return ONLY the JSON object.\n"
        f"caseId: {case['id']}\n"
        f"Post text:\n{case['text']}"
    )
    if provider == "anthropic":
        key = os.environ.get("ANTHROPIC_API_KEY")
        if not key:
            raise SystemExit("ANTHROPIC_API_KEY is required for --provider anthropic")
        body = {
            "model": os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5"),
            "max_tokens": 1500,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}],
        }
        request = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
            },
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
        text = payload["content"][0]["text"]
    elif provider == "openai":
        key = os.environ.get("OPENAI_API_KEY")
        if not key:
            raise SystemExit("OPENAI_API_KEY is required for --provider openai")
        body = {
            "model": os.environ.get("OPENAI_MODEL", "gpt-5.5"),
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        request = urllib.request.Request(
            "https://api.openai.com/v1/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "content-type": "application/json",
                "authorization": f"Bearer {key}",
            },
        )
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.loads(response.read().decode("utf-8"))
        text = payload["choices"][0]["message"]["content"]
    else:
        raise ValueError(f"Unknown provider: {provider}")

    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
        if text.endswith("json"):
            text = text[: -len("json")]
    return json.loads(text)


def baseline_reviewer_action(pipeline, thresholds, text: str) -> str:
    probability = float(pipeline.predict_proba([text])[0, 1])
    action = v2.decision_for_text(text, probability, thresholds)
    return BASELINE_TO_REVIEWER_ACTION[action]


def run(args: argparse.Namespace) -> dict:
    cases = json.loads(Path(args.cases).read_text(encoding="utf-8"))
    artifact = joblib.load(args.model_path)
    pipeline, thresholds = artifact["model"], artifact["thresholds"]

    if args.provider == "cached":
        cache = json.loads(Path(args.cache).read_text(encoding="utf-8"))
        provider_label = f"{cache['provider']} (cached {cache['generatedAt']})"
        extractions = [
            extraction_from_cache(case, cache["extractions"][case["id"]], provider_label)
            for case in cases
            if case["id"] in cache["extractions"]
        ]
    else:
        system_prompt = (REPO_ROOT / "llm_evidence/prompts/evidence_extractor_system.md").read_text(
            encoding="utf-8"
        )
        provider_label = args.provider
        extractions = []
        cache_out = {"provider": args.provider, "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "extractions": {}}
        for case in cases:
            raw = call_hosted_model(args.provider, system_prompt, case)
            cache_out["extractions"][case["id"]] = raw
            extractions.append(extraction_from_cache(case, raw, provider_label))
        if args.regenerate:
            Path(args.cache).write_text(
                json.dumps(cache_out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )

    # Stance showdown: real baseline false positives vs cached LLM stance reads.
    showcase = []
    error_path = Path(getattr(args, "error_analysis", "audit_outputs/error_analysis_report.json"))
    cache_payload = json.loads(Path(args.cache).read_text(encoding="utf-8"))
    fp_cache = cache_payload.get("fpShowcase", {})
    if error_path.exists() and fp_cache:
        error_report = json.loads(error_path.read_text(encoding="utf-8"))
        for fp in error_report.get("decisionLevelFalsePositives", []):
            entry = fp_cache.get(fp["caseId"])
            if not entry:
                continue
            showcase.append(
                {
                    "caseId": fp["caseId"],
                    "text": fp["text"],
                    "baselineAction": fp["action"],
                    "baselineScore": fp["score"],
                    "llmStance": entry["stance"],
                    "llmVerdict": entry["verdict"],
                    "llmAnalysis": entry["analysis"],
                }
            )

    case_by_id = {case["id"]: case for case in cases}
    per_case = []
    llm_pass = baseline_pass = agreement = faithful = 0
    for extraction in extractions:
        case = case_by_id[extraction["caseId"]]
        expected = expected_action(case)
        llm_action = extraction["recommendedReviewerAction"]
        base_action = baseline_reviewer_action(pipeline, thresholds, case["text"])
        llm_ok = action_passes(expected, llm_action)
        base_ok = action_passes(expected, base_action)
        llm_pass += llm_ok
        baseline_pass += base_ok
        agreement += llm_action == base_action
        faithful += extraction["faithfulness"]["allSpansFoundInSource"]
        per_case.append(
            {
                "caseId": case["id"],
                "groundTruth": case["ground_truth"],
                "expected": expected,
                "baseline": base_action,
                "llm": llm_action,
                "baselinePass": base_ok,
                "llmPass": llm_ok,
                "agree": llm_action == base_action,
                "confidence": extraction["confidence"],
                "spanFaithful": extraction["faithfulness"]["allSpansFoundInSource"],
                "reviewerSummary": extraction["reviewerSummary"],
            }
        )

    total = len(per_case)
    report = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "provider": provider_label,
        "caseCount": total,
        "llmExpectationPassRate": round(llm_pass / total, 4),
        "baselineExpectationPassRate": round(baseline_pass / total, 4),
        "actionAgreementRate": round(agreement / total, 4),
        "spanFaithfulnessRate": round(faithful / total, 4),
        "costModel": COST_MODEL,
        "stanceShowdown": showcase,
        "perCase": per_case,
        "extractions": extractions,
        "interpretation": (
            "Where the two disagree, the interesting cases are stance cases: the "
            "baseline keys on WHAT vocabulary appears, the LLM on WHO is speaking "
            "and WHY. The error-analysis report shows the baseline's largest real "
            "false-positive class is skeptical third-party reportage — exactly the "
            "stance distinction an LLM reads natively. That, not aggregate "
            "accuracy on this small suite, is the argument for LLM assistance on "
            "the review slice. The one scored disagreement (legit_wallet_help: "
            "suite expects review, the model chose no-action to avoid burdening a "
            "help-seeker) is preserved rather than tuned away — it is a live "
            "policy question, and pretending the tools agree would hide it."
        ),
    }
    return report


def to_markdown(report: dict) -> str:
    lines = [
        "# LLM Evidence Adapter — Baseline vs Hosted-Model Comparison",
        "",
        f"Provider: **{report['provider']}** · {report['caseCount']} cases · "
        f"generated {report['generatedAt']}",
        "",
        f"- LLM expectation pass rate: **{report['llmExpectationPassRate']:.0%}**",
        f"- Baseline expectation pass rate: **{report['baselineExpectationPassRate']:.0%}**",
        f"- Action agreement: **{report['actionAgreementRate']:.0%}**",
        f"- Span faithfulness (same gate as deterministic extractor): "
        f"**{report['spanFaithfulnessRate']:.0%}**",
        "",
        "## Economics",
        "",
        f"- Baseline: {report['costModel']['baselinePer1kPosts']}",
        f"- LLM: {report['costModel']['llmPer1kPosts']}",
        f"- Latency: {report['costModel']['llmLatencyPerPost']}",
        "",
        report["costModel"]["operationalNote"],
        "",
        "## Per-case outcomes",
        "",
        "| Case | Expected | Baseline | LLM | Agree |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in report["perCase"]:
        lines.append(
            f"| {row['caseId']} | {row['expected']} | {row['baseline']}"
            f"{'' if row['baselinePass'] else ' ❌'} | {row['llm']}"
            f"{'' if row['llmPass'] else ' ❌'} | {'yes' if row['agree'] else 'no'} |"
        )
    lines += ["", "## Interpretation", "", report["interpretation"], ""]
    return "\n".join(lines)


def to_lab_summary(report: dict) -> str:
    payload = {
        key: report[key]
        for key in (
            "generatedAt",
            "provider",
            "caseCount",
            "llmExpectationPassRate",
            "baselineExpectationPassRate",
            "actionAgreementRate",
            "spanFaithfulnessRate",
            "costModel",
            "stanceShowdown",
            "perCase",
            "interpretation",
        )
    }
    return "export const llmComparison = " + json.dumps(payload, indent=2, ensure_ascii=False) + ";\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", default="evals/scenario_eval_cases.json")
    parser.add_argument("--model-path", default="audit_outputs/fraud_labeler_v2.joblib")
    parser.add_argument("--cache", default="llm_evidence/cache/llm_evidence_cache.json")
    parser.add_argument("--error-analysis", default="audit_outputs/error_analysis_report.json")
    parser.add_argument("--provider", choices=["cached", "anthropic", "openai"], default="cached")
    parser.add_argument("--regenerate", action="store_true", help="Overwrite the cache with live outputs")
    parser.add_argument("--out", required=True)
    parser.add_argument("--markdown-out")
    parser.add_argument("--lab-summary")
    args = parser.parse_args()

    report = run(args)
    Path(args.out).write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if args.markdown_out:
        Path(args.markdown_out).write_text(to_markdown(report), encoding="utf-8")
    if args.lab_summary:
        Path(args.lab_summary).write_text(to_lab_summary(report), encoding="utf-8")

    print(
        json.dumps(
            {
                "provider": report["provider"],
                "llmPassRate": report["llmExpectationPassRate"],
                "baselinePassRate": report["baselineExpectationPassRate"],
                "spanFaithfulness": report["spanFaithfulnessRate"],
            },
            indent=2,
        )
    )
    # A broken cache (unfaithful spans) must fail the pipeline: cached
    # evidence that cannot be traced to source text is worse than none.
    return 0 if report["spanFaithfulnessRate"] == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
