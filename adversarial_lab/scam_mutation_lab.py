from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


ACTION_RANK = {
    "no_label": 0,
    "send_to_human_review": 1,
    "apply_potential_crypto_fraud_label": 2,
    "high_confidence_escalation": 3,
}
PUBLIC_LABEL_ACTIONS = {"apply_potential_crypto_fraud_label", "high_confidence_escalation"}


@dataclass(frozen=True)
class Mutation:
    id: str
    label: str
    category: str
    attack_goal: str
    standards: tuple[str, ...]
    apply: Callable[[str], str]


def replace_words(text: str, replacements: dict[str, str]) -> str:
    mutated = text
    for source, target in replacements.items():
        mutated = re.sub(rf"\b{re.escape(source)}\b", target, mutated, flags=re.IGNORECASE)
    return mutated


def spaced_keywords(text: str) -> str:
    return replace_words(
        text,
        {
            "wallet": "w a l l e t",
            "bitcoin": "b i t c o i n",
            "airdrop": "a i r d r o p",
            "claim": "c l a i m",
            "connect": "c o n n e c t",
            "crypto": "c r y p t o",
            "send": "s e n d",
            "deposit": "d e p o s i t",
        },
    )


def leetspeak(text: str) -> str:
    return replace_words(
        text,
        {
            "official": "0fficial",
            "verified": "ver1fied",
            "wallet": "w4llet",
            "bitcoin": "b1tc0in",
            "crypto": "crypt0",
            "free": "fr33",
            "claim": "cl4im",
            "connect": "c0nnect",
            "guaranteed": "guar4nteed",
            "returns": "r3turns",
            "deposit": "dep0sit",
        },
    )


def punctuation_stuffing(text: str) -> str:
    mutated = replace_words(
        text,
        {
            "claim": "c.l.a.i.m",
            "wallet": "wall-et",
            "airdrop": "air drop",
            "send": "s/e/n/d",
            "limited": "lim-ited",
            "deposit": "depo-sit",
            "guaranteed": "guaran-teed",
        },
    )
    return re.sub(r"\s+", "  ", mutated)


def defanged_url(text: str) -> str:
    mutated = re.sub(r"https://", "hxxps://", text, flags=re.IGNORECASE)
    mutated = re.sub(r"http://", "hxxp://", mutated, flags=re.IGNORECASE)
    mutated = re.sub(
        r"\b([a-z0-9-]+)\.(cash|click|com|io|net|org|top|xyz)\b",
        r"\1[.]\2",
        mutated,
        flags=re.IGNORECASE,
    )
    if mutated == text:
        mutated = f"{mutated} hxxps://secure-claim[.]xyz"
    return mutated


def brand_impersonation_shift(text: str) -> str:
    mutated = replace_words(
        text,
        {
            "Elon Musk": "Vitalik Foundation",
            "Microsoft": "Ledger Foundation",
            "Coinbase": "Coinbase Security",
            "Tesla": "Tesla Rewards",
            "Bitcoin": "BTC Foundation",
            "Ethereum": "ETH Foundation",
        },
    )
    return mutated if mutated != text else f"Verified partner notice: {text}"


def synonym_laundering(text: str) -> str:
    return replace_words(
        text,
        {
            "send": "transfer",
            "deposit": "fund",
            "connect": "sync",
            "wallet": "vault",
            "guaranteed": "assured",
            "free": "complimentary",
            "claim": "redeem",
            "processing fee": "release charge",
            "airdrop": "allocation",
            "giveaway": "community reward",
        },
    )


def screenshot_ocr(text: str) -> str:
    condensed = re.sub(r"\s+", " ", text).strip()
    return (
        "[Image OCR]\n"
        "Screenshot text: "
        f"{condensed}\n"
        "QR code visible. Link is partially cropped. Source account not visible."
    )


def context_laundering(text: str) -> str:
    mutated = replace_words(
        text,
        {
            "giveaway": "eligibility event",
            "airdrop": "eligibility event",
            "send": "confirm",
            "deposit": "confirm",
            "wallet": "account vault",
            "fee": "network check",
            "limited time": "eligibility window",
        },
    )
    return f"Support notice for eligible users: {mutated}"


MUTATIONS = (
    Mutation(
        id="spaced_keywords",
        label="Spaced keywords",
        category="lexical_obfuscation",
        attack_goal="Break exact keyword and n-gram matches while preserving the scam ask.",
        standards=("MITRE ATLAS: evasion testing", "NIST AI RMF Measure"),
        apply=spaced_keywords,
    ),
    Mutation(
        id="leetspeak",
        label="Leetspeak",
        category="lexical_obfuscation",
        attack_goal="Substitute visually similar characters to test char n-gram robustness.",
        standards=("MITRE ATLAS: evasion testing", "NIST AI RMF Measure"),
        apply=leetspeak,
    ),
    Mutation(
        id="punctuation_stuffing",
        label="Punctuation stuffing",
        category="lexical_obfuscation",
        attack_goal="Insert punctuation and spacing noise into enforcement-triggering terms.",
        standards=("MITRE ATLAS: evasion testing", "NIST CSF Detect"),
        apply=punctuation_stuffing,
    ),
    Mutation(
        id="defanged_url",
        label="Defanged URL",
        category="link_obfuscation",
        attack_goal="Hide risky domains behind hxxp and bracket-dot notation.",
        standards=("OWASP: untrusted content handling", "NIST CSF Detect"),
        apply=defanged_url,
    ),
    Mutation(
        id="brand_impersonation_shift",
        label="Brand shift",
        category="impersonation_variant",
        attack_goal="Move the same lure across brands or public entities.",
        standards=("Santa Clara Integrity", "NIST AI RMF Map"),
        apply=brand_impersonation_shift,
    ),
    Mutation(
        id="synonym_laundering",
        label="Synonym laundering",
        category="semantic_obfuscation",
        attack_goal="Replace policy-trigger words with softer funnel language.",
        standards=("MITRE ATLAS: robustness testing", "NIST AI RMF Measure"),
        apply=synonym_laundering,
    ),
    Mutation(
        id="screenshot_ocr",
        label="Screenshot OCR",
        category="multimodal_placeholder",
        attack_goal="Represent a scam as OCR from an image where source and link context are missing.",
        standards=("OWASP: multimodal content risk", "NIST AI RMF Map"),
        apply=screenshot_ocr,
    ),
    Mutation(
        id="context_laundering",
        label="Context laundering",
        category="semantic_obfuscation",
        attack_goal="Wrap the scam ask in support/eligibility language.",
        standards=("Santa Clara Understandable Rules", "NIST AI RMF Manage"),
        apply=context_laundering,
    ),
)


def load_cases(path: Path) -> list[dict[str, Any]]:
    cases = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(cases, list):
        raise ValueError("Cases file must contain a JSON list.")
    return cases


def seed_cases(cases: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    seeds = [
        case
        for case in cases
        if case.get("adversarial_seed") and case.get("ground_truth") == "fraud"
    ]
    return seeds[:limit]


def load_model(model_path: Path) -> tuple[object, dict[str, float]]:
    try:
        import joblib
        from policy_proposal_labeler_v2 import register_pickle_compatibility
    except ImportError as exc:
        raise SystemExit(
            "Install the v2 model dependencies before running the adversarial lab: "
            "pip install -r requirements-v2.txt"
        ) from exc
    if not model_path.exists():
        raise FileNotFoundError(f"Missing model artifact: {model_path}")
    register_pickle_compatibility()
    artifact = joblib.load(model_path)
    thresholds = artifact.get(
        "thresholds",
        {
            "review": artifact["threshold"],
            "label": artifact["threshold"],
            "high_confidence": artifact["threshold"],
        },
    )
    return artifact["model"], thresholds


def score_text(text: str, model: object, thresholds: dict[str, float]) -> dict[str, Any]:
    from policy_proposal_labeler_v2 import decision_for_text, policy_evidence, public_label_evidence

    probability = float(model.predict_proba([text])[0, 1])
    action = decision_for_text(text, probability, thresholds)
    public_evidence = public_label_evidence(text)
    evidence = policy_evidence(text)
    return {
        "probability": probability,
        "action": action,
        "actionRank": ACTION_RANK[action],
        "publicLabel": action in PUBLIC_LABEL_ACTIONS,
        "reviewOrLabel": action != "no_label",
        "policyScore": evidence["score"],
        "matchedRules": public_evidence["matched_rules"],
        "publicLabelRules": public_evidence["public_label_rules"],
    }


def variant_id(seed_id: str, mutation_id: str) -> str:
    return f"{seed_id}__{mutation_id}"


def build_variants(
    seeds: list[dict[str, Any]],
    model: object,
    thresholds: dict[str, float],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    baselines = []
    variants = []
    for seed in seeds:
        baseline_score = score_text(seed["text"], model, thresholds)
        baseline = {
            "id": seed["id"],
            "scenario": seed["scenario"],
            "tags": seed.get("tags", []),
            "text": seed["text"],
            **baseline_score,
        }
        baselines.append(baseline)
        for mutation in MUTATIONS:
            mutated_text = mutation.apply(seed["text"])
            mutated_score = score_text(mutated_text, model, thresholds)
            downgrade = baseline_score["actionRank"] - mutated_score["actionRank"]
            public_label_dropped = baseline_score["publicLabel"] and not mutated_score["publicLabel"]
            escaped = not mutated_score["reviewOrLabel"]
            severe_downgrade = baseline_score["publicLabel"] and mutated_score["action"] == "no_label"
            variants.append(
                {
                    "id": variant_id(seed["id"], mutation.id),
                    "seedId": seed["id"],
                    "scenario": seed["scenario"],
                    "mutationId": mutation.id,
                    "mutationLabel": mutation.label,
                    "category": mutation.category,
                    "attackGoal": mutation.attack_goal,
                    "standards": list(mutation.standards),
                    "changed": mutated_text != seed["text"],
                    "baseline": baseline_score,
                    "mutated": mutated_score,
                    "probabilityDelta": mutated_score["probability"] - baseline_score["probability"],
                    "actionDowngrade": max(0, downgrade),
                    "publicLabelDropped": public_label_dropped,
                    "escaped": escaped,
                    "severeDowngrade": severe_downgrade,
                    "originalText": seed["text"],
                    "mutatedText": mutated_text,
                    "tags": seed.get("tags", []),
                }
            )
    return baselines, variants


def summarize_by_mutation(variants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    mutation_meta = {mutation.id: mutation for mutation in MUTATIONS}
    for variant in variants:
        grouped[variant["mutationId"]].append(variant)

    summaries = []
    for mutation_id, items in grouped.items():
        count = len(items)
        public_retained = sum(1 for item in items if item["mutated"]["publicLabel"])
        review_retained = sum(1 for item in items if item["mutated"]["reviewOrLabel"])
        escapes = sum(1 for item in items if item["escaped"])
        downgraded = sum(1 for item in items if item["actionDowngrade"] > 0)
        severe = sum(1 for item in items if item["severeDowngrade"])
        avg_delta = sum(item["probabilityDelta"] for item in items) / max(1, count)
        worst = min(items, key=lambda item: (item["mutated"]["actionRank"], item["mutated"]["probability"]))
        mutation = mutation_meta[mutation_id]
        summaries.append(
            {
                "id": mutation_id,
                "label": mutation.label,
                "category": mutation.category,
                "attackGoal": mutation.attack_goal,
                "standards": list(mutation.standards),
                "variantCount": count,
                "publicLabelRetentionRate": public_retained / max(1, count),
                "reviewOrLabelRetentionRate": review_retained / max(1, count),
                "escapeCount": escapes,
                "downgradeCount": downgraded,
                "severeDowngradeCount": severe,
                "avgProbabilityDelta": avg_delta,
                "worstVariantId": worst["id"],
                "worstAction": worst["mutated"]["action"],
                "worstProbability": worst["mutated"]["probability"],
            }
        )
    return sorted(
        summaries,
        key=lambda item: (
            item["escapeCount"],
            item["severeDowngradeCount"],
            item["downgradeCount"],
            -item["reviewOrLabelRetentionRate"],
            -item["publicLabelRetentionRate"],
        ),
        reverse=True,
    )


def summarize_by_category(variants: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for variant in variants:
        grouped[variant["category"]].append(variant)
    return {
        category: {
            "variantCount": len(items),
            "escapeCount": sum(1 for item in items if item["escaped"]),
            "downgradeCount": sum(1 for item in items if item["actionDowngrade"] > 0),
            "reviewOrLabelRetentionRate": sum(1 for item in items if item["mutated"]["reviewOrLabel"]) / max(1, len(items)),
            "publicLabelRetentionRate": sum(1 for item in items if item["mutated"]["publicLabel"]) / max(1, len(items)),
        }
        for category, items in sorted(grouped.items())
    }


def standards_summary(variants: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for variant in variants:
        for standard in variant["standards"]:
            grouped[standard].append(variant)
    return {
        standard: {
            "variantCount": len(items),
            "escapeCount": sum(1 for item in items if item["escaped"]),
            "downgradeCount": sum(1 for item in items if item["actionDowngrade"] > 0),
        }
        for standard, items in sorted(grouped.items())
    }


def top_weaknesses(variants: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    ordered = sorted(
        variants,
        key=lambda item: (
            item["escaped"],
            item["severeDowngrade"],
            item["actionDowngrade"],
            -item["mutated"]["probability"],
            abs(item["probabilityDelta"]),
        ),
        reverse=True,
    )
    return [
        {
            "id": item["id"],
            "seedId": item["seedId"],
            "mutationLabel": item["mutationLabel"],
            "category": item["category"],
            "baselineAction": item["baseline"]["action"],
            "mutatedAction": item["mutated"]["action"],
            "baselineProbability": item["baseline"]["probability"],
            "mutatedProbability": item["mutated"]["probability"],
            "probabilityDelta": item["probabilityDelta"],
            "publicLabelDropped": item["publicLabelDropped"],
            "escaped": item["escaped"],
            "mutatedText": item["mutatedText"],
        }
        for item in ordered[:limit]
    ]


def build_report(
    cases_path: Path,
    model_path: Path,
    seeds: list[dict[str, Any]],
    baselines: list[dict[str, Any]],
    variants: list[dict[str, Any]],
    thresholds: dict[str, float],
) -> dict[str, Any]:
    mutation_summary = summarize_by_mutation(variants)
    action_counts = Counter(item["mutated"]["action"] for item in variants)
    public_label_retained = sum(1 for item in variants if item["mutated"]["publicLabel"])
    review_or_label_retained = sum(1 for item in variants if item["mutated"]["reviewOrLabel"])
    downgrade_count = sum(1 for item in variants if item["actionDowngrade"] > 0)
    escape_count = sum(1 for item in variants if item["escaped"])
    severe_downgrade_count = sum(1 for item in variants if item["severeDowngrade"])
    avg_probability_delta = sum(item["probabilityDelta"] for item in variants) / max(1, len(variants))

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "suite": "adversarial_scam_mutation_lab_v1",
        "caveat": (
            "This is a controlled red-team suite over authored scam seeds. It measures model and policy "
            "sensitivity to realistic evasion patterns; it is not a live-abuse benchmark."
        ),
        "casesPath": str(cases_path),
        "modelPath": str(model_path),
        "thresholds": thresholds,
        "seedCount": len(seeds),
        "mutationCount": len(MUTATIONS),
        "variantCount": len(variants),
        "publicLabelRetentionRate": public_label_retained / max(1, len(variants)),
        "reviewOrLabelRetentionRate": review_or_label_retained / max(1, len(variants)),
        "downgradeRate": downgrade_count / max(1, len(variants)),
        "escapeRate": escape_count / max(1, len(variants)),
        "severeDowngradeRate": severe_downgrade_count / max(1, len(variants)),
        "avgProbabilityDelta": avg_probability_delta,
        "actionCounts": dict(sorted(action_counts.items())),
        "mutationSummary": mutation_summary,
        "categorySummary": summarize_by_category(variants),
        "standardsSummary": standards_summary(variants),
        "topWeaknesses": top_weaknesses(variants),
        "baselines": baselines,
        "variants": variants,
    }


def compact_lab_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "generatedAt": report["generatedAt"],
        "suite": report["suite"],
        "seedCount": report["seedCount"],
        "mutationCount": report["mutationCount"],
        "variantCount": report["variantCount"],
        "publicLabelRetentionRate": report["publicLabelRetentionRate"],
        "reviewOrLabelRetentionRate": report["reviewOrLabelRetentionRate"],
        "downgradeRate": report["downgradeRate"],
        "escapeRate": report["escapeRate"],
        "severeDowngradeRate": report["severeDowngradeRate"],
        "avgProbabilityDelta": report["avgProbabilityDelta"],
        "actionCounts": report["actionCounts"],
        "mutationSummary": report["mutationSummary"],
        "categorySummary": report["categorySummary"],
        "topWeaknesses": report["topWeaknesses"][:5],
    }


def write_lab_summary(path: Path, summary: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(summary, ensure_ascii=False, indent=2)
    path.write_text(f"export const adversarialLab = {rendered};\n", encoding="utf-8")


def pct(value: float) -> str:
    return f"{value * 100:.1f}%"


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Adversarial Scam Lab Report",
        "",
        f"Generated: {report['generatedAt']}",
        "",
        "## Summary",
        "",
        f"- Seed scam cases: {report['seedCount']}",
        f"- Mutation operators: {report['mutationCount']}",
        f"- Mutated variants: {report['variantCount']}",
        f"- Public-label retention: {pct(report['publicLabelRetentionRate'])}",
        f"- Review-or-label retention: {pct(report['reviewOrLabelRetentionRate'])}",
        f"- Downgrade rate: {pct(report['downgradeRate'])}",
        f"- Escape rate: {pct(report['escapeRate'])}",
        f"- Severe downgrade rate: {pct(report['severeDowngradeRate'])}",
        f"- Average probability delta: {report['avgProbabilityDelta']:.3f}",
        "",
        "Interpretation: review-or-label retention is the recall-first safety metric. Public-label retention is stricter, because some adversarial posts may be better routed to human review before public enforcement.",
        "",
        "## Mutation Results",
        "",
        "| Mutation | Category | Variants | Public-label retained | Review/label retained | Escapes | Downgrades | Worst action |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for item in report["mutationSummary"]:
        lines.append(
            "| {label} | {category} | {count} | {public_rate} | {review_rate} | {escapes} | {downgrades} | {worst} |".format(
                label=item["label"],
                category=item["category"],
                count=item["variantCount"],
                public_rate=pct(item["publicLabelRetentionRate"]),
                review_rate=pct(item["reviewOrLabelRetentionRate"]),
                escapes=item["escapeCount"],
                downgrades=item["downgradeCount"],
                worst=item["worstAction"],
            )
        )
    lines.extend(
        [
            "",
            "## Top Weaknesses",
            "",
        ]
    )
    for item in report["topWeaknesses"]:
        lines.extend(
            [
                f"### {item['id']}",
                "",
                f"- Mutation: {item['mutationLabel']}",
                f"- Baseline action: {item['baselineAction']}",
                f"- Mutated action: {item['mutatedAction']}",
                f"- Probability delta: {item['probabilityDelta']:.3f}",
                f"- Public label dropped: {item['publicLabelDropped']}",
                f"- Escaped review/label: {item['escaped']}",
                "",
                "```text",
                item["mutatedText"],
                "```",
                "",
            ]
        )
    lines.extend(
        [
            "## Standards Mapping",
            "",
            "| Standard / Frame | Variants | Escapes | Downgrades |",
            "| --- | ---: | ---: | ---: |",
        ]
    )
    for standard, summary in report["standardsSummary"].items():
        lines.append(
            f"| {standard} | {summary['variantCount']} | {summary['escapeCount']} | {summary['downgradeCount']} |"
        )
    lines.extend(
        [
            "",
            "## Next Controls",
            "",
            "- Add canonicalization before scoring: normalize leetspeak, defanged URLs, bracket-dot domains, and spaced scam keywords.",
            "- Add OCR-specific review routing when source account, link target, or QR destination is missing.",
            "- Add URL expansion and landing-page analysis before public enforcement.",
            "- Track mutation failures as regression tests in CI before changing thresholds or model features.",
        ]
    )
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description="Controlled adversarial mutation lab for crypto-scam moderation.")
    parser.add_argument("--cases", default=str(ROOT / "evals" / "scenario_eval_cases.json"))
    parser.add_argument("--model-path", default=str(ROOT / "audit_outputs" / "fraud_labeler_v2.joblib"))
    parser.add_argument("--out", default=str(ROOT / "audit_outputs" / "adversarial_scam_lab_report.json"))
    parser.add_argument("--markdown-out", default=str(ROOT / "audit_outputs" / "adversarial_scam_lab_report.md"))
    parser.add_argument("--lab-summary", default=str(ROOT / "crypto-scam-lab" / "data" / "adversarialLab.js"))
    parser.add_argument("--max-seed-cases", type=int, default=7)
    args = parser.parse_args()

    cases_path = Path(args.cases)
    model_path = Path(args.model_path)
    cases = load_cases(cases_path)
    seeds = seed_cases(cases, args.max_seed_cases)
    model, thresholds = load_model(model_path)
    baselines, variants = build_variants(seeds, model, thresholds)
    report = build_report(cases_path, model_path, seeds, baselines, variants, thresholds)

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
