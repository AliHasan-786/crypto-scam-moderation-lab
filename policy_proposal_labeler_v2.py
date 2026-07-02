from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import joblib
import numpy as np
from scipy import sparse
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import FeatureUnion, Pipeline


LABEL_NAME = "Potential Crypto Fraud"


@dataclass(frozen=True)
class PolicyRule:
    name: str
    weight: float
    description: str
    patterns: tuple[str, ...]


POLICY_RULES = (
    PolicyRule(
        name="unrealistic_returns",
        weight=0.24,
        description="Guaranteed, risk-free, doubled, or implausibly high short-term gains.",
        patterns=(
            r"guaranteed",
            r"risk[-\s]?free",
            r"sin riesgo",
            r"ganancias? garantizadas?",
            r"rendimientos? garantizados?",
            r"double your",
            r"duplica",
            r"\b[0-9]{2,}\s?%",
            r"\b[0-9]+x\b",
            r"instant(?:ly)?",
            r"passive income",
            r"profits?",
            r"returns?",
        ),
    ),
    PolicyRule(
        name="crypto_transfer_request",
        weight=0.23,
        description="Direct requests to send crypto, pay fees, deposit funds, or connect a wallet.",
        patterns=(
            r"send\s+(?:me\s+)?(?:[0-9.]+\s*)?(btc|bitcoin|eth|ethereum|sol|usdt|crypto)",
            r"sending\s+(?:[0-9.]+\s*)?(btc|bitcoin|eth|ethereum|sol|usdt|crypto)",
            r"send .* wallet",
            r"envia\s+(?:[0-9.]+\s*)?(btc|bitcoin|eth|ethereum|sol|usdt|cripto)",
            r"enviar\s+(?:[0-9.]+\s*)?(btc|bitcoin|eth|ethereum|sol|usdt|cripto)",
            r"\baddress:\s*[a-z0-9]",
            r"wallet address",
            r"connect your wallet",
            r"conecta tu (wallet|billetera)",
            r"conectar tu (wallet|billetera)",
            r"processing fee",
            r"upfront",
            r"deposit",
            r"verify your wallet",
            r"verifica tu (wallet|billetera)",
        ),
    ),
    PolicyRule(
        name="suspicious_giveaway",
        weight=0.19,
        description="Giveaways, airdrops, promo codes, free tokens, and prize/claim language.",
        patterns=(
            r"airdrop",
            r"giveaway",
            r"claim",
            r"reclama",
            r"winner",
            r"prize",
            r"premio",
            r"congratulations",
            r"promo code",
            r"free\s+(btc|bitcoin|eth|ethereum|usdt|crypto|token)",
            r"(btc|bitcoin|eth|ethereum|usdt|cripto|token)\s+gratis",
            r"bonus",
            r"bono",
        ),
    ),
    PolicyRule(
        name="authority_misuse",
        weight=0.13,
        description="Official, verified, celebrity, exchange, or major-brand authority claims.",
        patterns=(
            r"official",
            r"verified",
            r"oficial",
            r"verificado",
            r"\belon\b|\bmusk\b|bill gates|microsoft|ronaldo|cr7",
            r"coinbase|binance|meta|tesla",
            r"support escalation",
            r"account restriction",
            r"founder",
            r"\bceo\b",
        ),
    ),
    PolicyRule(
        name="urgency_or_scarcity",
        weight=0.11,
        description="Time pressure, scarcity, or strong call-to-action phrasing.",
        patterns=(
            r"limited",
            r"expires?",
            r"expira",
            r"urgent",
            r"act now",
            r"hurry",
            r"spots? available",
            r"before it closes",
            r"immediately",
            r"ahora",
            r"ultima oportunidad",
        ),
    ),
    PolicyRule(
        name="risky_link_surface",
        weight=0.10,
        description="Suspicious campaign domains, URL shorteners, or wallet-drainer-style links.",
        patterns=(
            r"https?://",
            r"\b[a-z0-9-]+\.(cash|io|net|xyz|top|click)\b",
            r"\b[a-z0-9-]*(winner|airdrop|giveaway|secure|crypto|verify|wallet|security)[a-z0-9-]*\.[a-z]{2,}\b",
            r"bit\.ly|tinyurl|t\.co",
        ),
    ),
)


FINANCIAL_TERMS = (
    "bitcoin",
    "btc",
    "ethereum",
    "eth",
    "crypto",
    "token",
    "wallet",
    "airdrop",
    "staking",
    "trading",
    "investment",
    "profit",
    "return",
    "usdt",
    "cripto",
    "billetera",
    "defi",
    "exchange",
)

PUBLIC_LABEL_RULES = frozenset(
    {
        "unrealistic_returns",
        "crypto_transfer_request",
        "suspicious_giveaway",
        "urgency_or_scarcity",
        "risky_link_surface",
    }
)

PROTECTIVE_CONTEXT_PATTERNS = (
    r"\bdo not send\b",
    r"\bdon't send\b",
    r"\bavoid\b.*\bscams?\b",
    r"\bwarn(?:ed|ing|s)?\b.*\bscams?\b",
    r"\bscam warning\b",
    r"\banti[-\s]?scam\b",
    r"\bfraud research\b",
    r"\bresearch\b",
    r"\bstud(?:y|ies)\b",
    r"\bpaper\b",
    r"\bnot investment advice\b",
    r"\bgovernance\b.*\bairdrop\b",
    r"\bno claim page\b",
    r"\bnot sharing\b.*\bwallet link\b",
    r"\bno envies\b.*\b(cripto|btc|eth|usdt|wallet|billetera)\b",
    r"\bno conectes\b.*\b(wallet|billetera)\b",
    r"\b(alerta|advertencia)\b.*\b(estafa|scam|cripto|wallet|billetera)\b",
)

SATIRE_CONTEXT_PATTERNS = (
    r"\bobviously not\b",
    r"\bimaginary\b",
    r"\bsatire\b",
    r"\bjoke\b",
)

DEVELOPER_CONTEXT_PATTERNS = (
    r"\bdebug(?:ging)?\b",
    r"\btestnet\b",
    r"\bstale session\b",
    r"\bbug\b",
    r"\bdeveloper\b",
    r"\bsecurity problem\b",
)

UNCERTAIN_REVIEW_PATTERNS = (
    r"\bnot verified\b",
    r"\bcannot tell\b",
    r"\bcan't tell\b",
    r"\bhas anyone\b",
    r"\banyone know\b",
    r"\bis it legit\b",
    r"\bsafely\b",
    r"\bno visible source\b",
    r"\bimage ocr\b",
    r"\blink is cropped\b",
    r"\bsource account not visible\b",
    r"\bredirects?\b",
    r"\bdifferent website\b",
    r"\balguien sabe\b",
    r"\bno he verificado\b",
    r"\bredirige\b",
)

WALLETISH_PATTERN = re.compile(
    r"(0x[a-f0-9]{20,}|bc1[a-z0-9]{20,}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|[A-Za-z0-9]{24,})",
    re.IGNORECASE,
)


def normalize_text(text: object) -> str:
    return re.sub(r"\s+", " ", str(text or "").strip().strip('"')).strip()


def strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    return "".join(char for char in normalized if not unicodedata.combining(char))


def canonicalize_for_policy(text: object) -> str:
    """Normalize common scam obfuscation before deterministic policy matching."""
    value = strip_accents(normalize_text(text))
    replacements = (
        (r"hxxps?://", "https://"),
        (r"\[\.\]|\(\.\)|\{\.\}", "."),
        (r"\s+(?:dot|\[dot\]|\(dot\))\s+", "."),
        (r"\bw\s*[\s.\-]*a\s*[\s.\-]*l\s*[\s.\-]*l\s*[\s.\-]*e\s*[\s.\-]*t\b", "wallet"),
        (r"\bc\s*[\s.\-]*o\s*[\s.\-]*n\s*[\s.\-]*n\s*[\s.\-]*e\s*[\s.\-]*c\s*[\s.\-]*t\b", "connect"),
        (r"\bc\s*[\s.\-]*l\s*[\s.\-]*a\s*[\s.\-]*i\s*[\s.\-]*m\b", "claim"),
        (r"\ba\s*[\s.\-]*i\s*[\s.\-]*r\s*[\s.\-]*d\s*[\s.\-]*r\s*[\s.\-]*o\s*[\s.\-]*p\b", "airdrop"),
        (r"\bb\s*[\s.\-]*i\s*[\s.\-]*t\s*[\s.\-]*c\s*[\s.\-]*o\s*[\s.\-]*i\s*[\s.\-]*n\b", "bitcoin"),
        (r"\bc\s*[\s.\-]*r\s*[\s.\-]*y\s*[\s.\-]*p\s*[\s.\-]*t\s*[\s.\-]*o\b", "crypto"),
        (r"\bs\s*[\s.\-]*e\s*[\s.\-]*n\s*[\s.\-]*d\b", "send"),
        (r"\bw4llet\b", "wallet"),
        (r"\bwall-et\b", "wallet"),
        (r"\bcrypt0\b", "crypto"),
        (r"\bb1tc0in\b", "bitcoin"),
        (r"\b0fficial\b", "official"),
        (r"\bc0inbase\b", "coinbase"),
        (r"\bcl4im\b", "claim"),
        (r"\bc0nnect\b", "connect"),
        (r"\bfr33\b", "free"),
        (r"\bguar4nteed\b", "guaranteed"),
    )
    for pattern, replacement in replacements:
        value = re.sub(pattern, replacement, value, flags=re.IGNORECASE)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def read_labeled_csv(path: str | Path) -> tuple[list[str], np.ndarray]:
    texts: list[str] = []
    labels: list[int] = []
    with Path(path).open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"Post Content", "Ground Truth Label"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"{path} must contain columns: {sorted(required)}")
        for row in reader:
            raw_label = str(row.get("Ground Truth Label", "")).strip()
            if raw_label not in {"0", "1"}:
                continue
            texts.append(normalize_text(row.get("Post Content", "")))
            labels.append(int(raw_label))
    return texts, np.asarray(labels, dtype=int)


def _pattern_hit_count(text: str, patterns: Iterable[str]) -> int:
    return sum(1 for pattern in patterns if re.search(pattern, text, re.IGNORECASE))


def policy_evidence(text: str) -> dict[str, object]:
    normalized = normalize_text(text)
    canonicalized = canonicalize_for_policy(normalized)
    lower = canonicalized.lower()
    rule_details = []
    score = 0.06 if normalized else 0.0

    for rule in POLICY_RULES:
        hits = _pattern_hit_count(canonicalized, rule.patterns)
        matched = hits > 0
        contribution = rule.weight if matched else 0.0
        score += contribution
        rule_details.append(
            {
                "name": rule.name,
                "description": rule.description,
                "matched": matched,
                "hits": hits,
                "contribution": contribution,
            }
        )

    finance_hits = sum(1 for term in FINANCIAL_TERMS if term in lower)
    walletish = bool(WALLETISH_PATTERN.search(normalized) or WALLETISH_PATTERN.search(canonicalized))
    uppercase_ratio = (
        sum(1 for char in normalized if "A" <= char <= "Z") / max(1, len(normalized))
    )
    digit_ratio = sum(1 for char in normalized if char.isdigit()) / max(1, len(normalized))
    score += min(0.10, finance_hits * 0.018)
    score += 0.08 if walletish else 0.0
    score += 0.025 if uppercase_ratio > 0.12 else 0.0
    score = min(0.98, score)

    return {
        "label": LABEL_NAME,
        "score": score,
        "rules": rule_details,
        "finance_term_count": finance_hits,
        "walletish_string": walletish,
        "uppercase_ratio": uppercase_ratio,
        "digit_ratio": digit_ratio,
        "word_count": len(normalized.split()),
        "canonicalized_text": canonicalized,
        "canonicalization_applied": canonicalized != strip_accents(normalized),
    }


class PolicyFeatureTransformer(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X):
        rows = []
        for text in X:
            evidence = policy_evidence(text)
            rule_values = [rule["contribution"] for rule in evidence["rules"]]
            rows.append(
                rule_values
                + [
                    evidence["score"],
                    min(1.0, evidence["finance_term_count"] / 8),
                    1.0 if evidence["walletish_string"] else 0.0,
                    evidence["uppercase_ratio"],
                    evidence["digit_ratio"],
                    min(1.0, evidence["word_count"] / 80),
                ]
            )
        return sparse.csr_matrix(np.asarray(rows, dtype=float))


def register_pickle_compatibility() -> None:
    """Make joblib artifacts portable when this file is run as a script."""
    module_name = "policy_proposal_labeler_v2"
    sys.modules.setdefault(module_name, sys.modules[__name__])
    PolicyRule.__module__ = module_name
    PolicyFeatureTransformer.__module__ = module_name

    main_module = sys.modules.get("__main__")
    if main_module is not None:
        setattr(main_module, "PolicyRule", PolicyRule)
        setattr(main_module, "PolicyFeatureTransformer", PolicyFeatureTransformer)


def make_model() -> Pipeline:
    features = FeatureUnion(
        transformer_list=[
            (
                "word_tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    ngram_range=(1, 3),
                    min_df=1,
                    max_df=0.95,
                    max_features=8000,
                    stop_words="english",
                    sublinear_tf=True,
                ),
            ),
            (
                "char_tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=1,
                    max_features=6000,
                    sublinear_tf=True,
                ),
            ),
            ("policy_features", PolicyFeatureTransformer()),
        ]
    )
    return Pipeline(
        steps=[
            ("features", features),
            (
                "classifier",
                LogisticRegression(
                    C=1.0,
                    class_weight="balanced",
                    max_iter=2000,
                    random_state=42,
                    solver="liblinear",
                ),
            ),
        ]
    )


def tune_threshold_oof(
    texts: list[str],
    labels: np.ndarray,
    *,
    target_precision: float = 0.75,
) -> tuple[float, dict[str, float]]:
    min_class = int(np.bincount(labels).min())
    folds = max(2, min(5, min_class))
    cv = StratifiedKFold(n_splits=folds, shuffle=True, random_state=42)
    probabilities = np.zeros(len(labels), dtype=float)

    for train_idx, valid_idx in cv.split(texts, labels):
        model = make_model()
        train_texts = [texts[i] for i in train_idx]
        valid_texts = [texts[i] for i in valid_idx]
        model.fit(train_texts, labels[train_idx])
        probabilities[valid_idx] = model.predict_proba(valid_texts)[:, 1]

    candidates = []
    for threshold in np.linspace(0.05, 0.95, 91):
        pred = (probabilities >= threshold).astype(int)
        precision = precision_score(labels, pred, zero_division=0)
        recall = recall_score(labels, pred, zero_division=0)
        f1 = f1_score(labels, pred, zero_division=0)
        candidates.append(
            {
                "threshold": float(threshold),
                "precision": float(precision),
                "recall": float(recall),
                "f1": float(f1),
            }
        )

    eligible = [item for item in candidates if item["precision"] >= target_precision]
    pool = eligible or candidates
    best = max(pool, key=lambda item: (item["f1"], item["recall"], -item["threshold"]))
    return best["threshold"], best


def evaluate_predictions(
    labels: np.ndarray,
    probabilities: np.ndarray,
    threshold: float,
) -> dict[str, object]:
    predictions = (probabilities >= threshold).astype(int)
    matrix = confusion_matrix(labels, predictions, labels=[0, 1])
    report = classification_report(
        labels,
        predictions,
        target_names=["Legitimate", "Potential Crypto Fraud"],
        zero_division=0,
        output_dict=True,
    )
    result = {
        "threshold": threshold,
        "accuracy": float(accuracy_score(labels, predictions)),
        "precision": float(precision_score(labels, predictions, zero_division=0)),
        "recall": float(recall_score(labels, predictions, zero_division=0)),
        "f1": float(f1_score(labels, predictions, zero_division=0)),
        "confusion_matrix": {
            "tn": int(matrix[0, 0]),
            "fp": int(matrix[0, 1]),
            "fn": int(matrix[1, 0]),
            "tp": int(matrix[1, 1]),
        },
        "classification_report": report,
    }
    try:
        result["roc_auc"] = float(roc_auc_score(labels, probabilities))
    except ValueError:
        result["roc_auc"] = None
    return result


def decision_for_probability(probability: float, thresholds: dict[str, float]) -> str:
    if probability >= thresholds["high_confidence"]:
        return "high_confidence_escalation"
    if probability >= thresholds["label"]:
        return "apply_potential_crypto_fraud_label"
    if probability >= thresholds["review"]:
        return "send_to_human_review"
    return "no_label"


def public_label_evidence(text: str) -> dict[str, object]:
    evidence = policy_evidence(text)
    matched_rules = [
        rule["name"]
        for rule in evidence["rules"]
        if rule["matched"]
    ]
    public_label_rules = [
        rule_name
        for rule_name in matched_rules
        if rule_name in PUBLIC_LABEL_RULES
    ]
    return {
        "has_public_label_evidence": bool(public_label_rules),
        "matched_rules": matched_rules,
        "public_label_rules": public_label_rules,
    }


def contextual_safety_evidence(text: str) -> dict[str, object]:
    normalized = canonicalize_for_policy(text)
    protective = _pattern_hit_count(normalized, PROTECTIVE_CONTEXT_PATTERNS) > 0
    satire = _pattern_hit_count(normalized, SATIRE_CONTEXT_PATTERNS) > 0
    developer = _pattern_hit_count(normalized, DEVELOPER_CONTEXT_PATTERNS) > 0
    uncertain_review = _pattern_hit_count(normalized, UNCERTAIN_REVIEW_PATTERNS) > 0
    return {
        "protective_or_research_context": protective,
        "satire_context": satire,
        "developer_context": developer,
        "uncertain_review_context": uncertain_review,
        "public_label_suppressed": protective or satire or developer,
        "review_preferred": uncertain_review,
    }


def decision_for_text(text: str, probability: float, thresholds: dict[str, float]) -> str:
    label_evidence = public_label_evidence(text)
    context = contextual_safety_evidence(text)
    can_publicly_label = bool(label_evidence["has_public_label_evidence"])

    if context["public_label_suppressed"]:
        return "no_label"
    if context["review_preferred"] and (
        can_publicly_label or probability >= max(0.20, thresholds["review"] - 0.15)
    ):
        return "send_to_human_review"

    if probability >= thresholds["high_confidence"] and can_publicly_label:
        return "high_confidence_escalation"
    if probability >= thresholds["label"] and can_publicly_label:
        return "apply_potential_crypto_fraud_label"
    if probability >= thresholds["review"]:
        return "send_to_human_review"
    return "no_label"


def evaluate_action_policy(
    texts: list[str],
    labels: np.ndarray,
    probabilities: np.ndarray,
    thresholds: dict[str, float],
) -> dict[str, object]:
    actions = [decision_for_text(text, float(prob), thresholds) for text, prob in zip(texts, probabilities)]
    auto_label_predictions = np.asarray(
        [
            action in {"apply_potential_crypto_fraud_label", "high_confidence_escalation"}
            for action in actions
        ],
        dtype=int,
    )
    review_or_label_predictions = np.asarray(
        [action != "no_label" for action in actions],
        dtype=int,
    )

    label_matrix = confusion_matrix(labels, auto_label_predictions, labels=[0, 1])
    review_matrix = confusion_matrix(labels, review_or_label_predictions, labels=[0, 1])
    action_counts = {action: actions.count(action) for action in sorted(set(actions))}

    return {
        "policy_guardrail": "Public labels require both model confidence and concrete scam-policy evidence.",
        "public_label_metrics": {
            "precision": float(precision_score(labels, auto_label_predictions, zero_division=0)),
            "recall": float(recall_score(labels, auto_label_predictions, zero_division=0)),
            "f1": float(f1_score(labels, auto_label_predictions, zero_division=0)),
            "confusion_matrix": {
                "tn": int(label_matrix[0, 0]),
                "fp": int(label_matrix[0, 1]),
                "fn": int(label_matrix[1, 0]),
                "tp": int(label_matrix[1, 1]),
            },
        },
        "review_or_label_metrics": {
            "precision": float(precision_score(labels, review_or_label_predictions, zero_division=0)),
            "recall": float(recall_score(labels, review_or_label_predictions, zero_division=0)),
            "f1": float(f1_score(labels, review_or_label_predictions, zero_division=0)),
            "confusion_matrix": {
                "tn": int(review_matrix[0, 0]),
                "fp": int(review_matrix[0, 1]),
                "fn": int(review_matrix[1, 0]),
                "tp": int(review_matrix[1, 1]),
            },
        },
        "action_counts": action_counts,
    }


def evaluate_policy_rules(texts: list[str], labels: np.ndarray) -> dict[str, object]:
    scores = np.asarray([policy_evidence(text)["score"] for text in texts], dtype=float)
    best = max(
        (
            {
                "threshold": float(threshold),
                "f1": float(f1_score(labels, scores >= threshold, zero_division=0)),
                "precision": float(
                    precision_score(labels, scores >= threshold, zero_division=0)
                ),
                "recall": float(recall_score(labels, scores >= threshold, zero_division=0)),
            }
            for threshold in np.linspace(0.05, 0.95, 91)
        ),
        key=lambda item: (item["f1"], item["recall"]),
    )
    result = evaluate_predictions(labels, scores, best["threshold"])
    result["tuned_on"] = "same_split"
    return result


def train_and_evaluate(
    train_csv: str | Path = "data.csv",
    test_csv: str | Path = "test.csv",
    model_path: str | Path = "fraud_labeler_v2.joblib",
) -> dict[str, object]:
    register_pickle_compatibility()
    train_texts, y_train = read_labeled_csv(train_csv)
    test_texts, y_test = read_labeled_csv(test_csv)
    threshold_targets = {
        "review": 0.75,
        "label": 0.85,
        "high_confidence": 0.90,
    }
    threshold_floors = {
        # Avoid architecture-level numeric drift around a fragile OOF boundary.
        "review": 0.40,
    }
    threshold_details_by_tier = {}
    thresholds = {}
    for tier, target_precision in threshold_targets.items():
        threshold, details = tune_threshold_oof(
            train_texts,
            y_train,
            target_precision=target_precision,
        )
        raw_threshold = threshold
        threshold = max(threshold, threshold_floors.get(tier, 0.0))
        details = {
            **details,
            "raw_threshold": raw_threshold,
            "policy_floor": threshold_floors.get(tier),
            "threshold": threshold,
        }
        thresholds[tier] = threshold
        threshold_details_by_tier[tier] = details

    model = make_model()
    model.fit(train_texts, y_train)
    test_probabilities = model.predict_proba(test_texts)[:, 1]
    test_metrics_by_tier = {
        tier: evaluate_predictions(y_test, test_probabilities, threshold)
        for tier, threshold in thresholds.items()
    }

    artifact = {
        "model": model,
        "threshold": thresholds["label"],
        "thresholds": thresholds,
        "label": LABEL_NAME,
        "policy_rules": POLICY_RULES,
        "public_label_rules": sorted(PUBLIC_LABEL_RULES),
    }
    joblib.dump(artifact, model_path)

    return {
        "train_csv": str(train_csv),
        "test_csv": str(test_csv),
        "model_path": str(model_path),
        "train_rows": len(train_texts),
        "test_rows": len(test_texts),
        "threshold_tuning": threshold_details_by_tier,
        "test_metrics": test_metrics_by_tier["label"],
        "test_metrics_by_tier": test_metrics_by_tier,
        "test_operational_policy": evaluate_action_policy(
            test_texts,
            y_test,
            test_probabilities,
            thresholds,
        ),
        "policy_rule_baseline_train": evaluate_policy_rules(train_texts, y_train),
        "policy_rule_baseline_test": evaluate_policy_rules(test_texts, y_test),
    }


def predict_text(text: str, model_path: str | Path = "fraud_labeler_v2.joblib") -> dict[str, object]:
    register_pickle_compatibility()
    artifact = joblib.load(model_path)
    probability = float(artifact["model"].predict_proba([text])[:, 1][0])
    thresholds = artifact.get("thresholds", {"review": artifact["threshold"], "label": artifact["threshold"], "high_confidence": artifact["threshold"]})
    threshold = float(thresholds["label"])
    return {
        "label": artifact["label"],
        "probability": probability,
        "threshold": threshold,
        "thresholds": thresholds,
        "prediction": int(probability >= threshold),
        "action": decision_for_text(text, probability, thresholds),
        "public_label_evidence": public_label_evidence(text),
        "contextual_safety_evidence": contextual_safety_evidence(text),
        "evidence": policy_evidence(text),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Reproducible crypto-fraud labeler v2")
    subparsers = parser.add_subparsers(dest="command")

    eval_parser = subparsers.add_parser("evaluate", help="Train and evaluate v2")
    eval_parser.add_argument("--train", default="data.csv")
    eval_parser.add_argument("--test", default="test.csv")
    eval_parser.add_argument("--model-path", default="fraud_labeler_v2.joblib")
    eval_parser.add_argument("--out", default="")

    pred_parser = subparsers.add_parser("predict", help="Predict one text")
    pred_parser.add_argument("--text", required=True)
    pred_parser.add_argument("--model-path", default="fraud_labeler_v2.joblib")

    args = parser.parse_args()
    if args.command in {None, "evaluate"}:
        result = train_and_evaluate(args.train, args.test, args.model_path)
        rendered = json.dumps(result, indent=2)
        if args.out:
            Path(args.out).write_text(rendered + "\n", encoding="utf-8")
        print(rendered)
    elif args.command == "predict":
        print(json.dumps(predict_text(args.text, args.model_path), indent=2))


if __name__ == "__main__":
    main()
