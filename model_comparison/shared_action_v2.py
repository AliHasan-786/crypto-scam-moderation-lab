"""Offline-only shared-action adapter for the preregistered V2 comparator.

This module deliberately has no provider client or network dependency. It
validates a provider-shaped response, applies the frozen policy guard, and
supports deterministic fixture replay only.
"""
from __future__ import annotations

import csv
import hashlib
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from policy_proposal_labeler_v2 import (
    PUBLIC_LABEL_RULES,
    contextual_safety_evidence,
    policy_evidence,
    register_pickle_compatibility,
)

ACTIONS = frozenset({"public_label_candidate", "human_review", "no_action"})
PROTECTED_CONTEXTS = frozenset(
    {"warning", "reportage", "satire", "research", "debugging", "help_seeking"}
)
EXPECTED_TEST_SHA256 = "b886ac28c805e6ed8cabb74f6fa24551467bb2d7bdba5cfda2ecec0392685a14"
EXPECTED_TEST_ROWS = 168


class SharedActionError(ValueError):
    """Raised when a record cannot participate in the shared-action contract."""


@dataclass(frozen=True)
class SharedActionResult:
    action: str | None
    compatible: bool
    incompatibility_reason: str | None
    speaker_originated_evidence: list[str]
    risk_indicators: list[str]
    protected_context: list[str]
    rationale: str | None
    adjustment: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load_pinned_test_rows(path: Path) -> list[dict[str, str]]:
    """Load only the preregistered V2 corpus identity, never an arbitrary CSV."""
    if sha256(path.read_bytes()) != EXPECTED_TEST_SHA256:
        raise SharedActionError("V2 replay corpus hash does not match the preregistered test.csv")
    with path.open(encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != EXPECTED_TEST_ROWS:
        raise SharedActionError("V2 replay corpus row count does not match the preregistered test.csv")
    return rows


def _string_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
        raise SharedActionError(f"{field} must be a list of non-empty strings")
    return [item.strip() for item in value]


def _incompatible(reason: str) -> SharedActionResult:
    return SharedActionResult(
        action=None,
        compatible=False,
        incompatibility_reason=reason,
        speaker_originated_evidence=[],
        risk_indicators=[],
        protected_context=[],
        rationale=None,
        adjustment=None,
    )


def _apply_policy_guard(
    *,
    action: str,
    speaker_originated_evidence: list[str],
    risk_indicators: list[str],
    protected_context: list[str],
    rationale: str,
) -> SharedActionResult:
    if action == "public_label_candidate":
        if protected_context:
            return SharedActionResult(
                action="human_review",
                compatible=True,
                incompatibility_reason=None,
                speaker_originated_evidence=speaker_originated_evidence,
                risk_indicators=risk_indicators,
                protected_context=protected_context,
                rationale=rationale,
                adjustment="downgraded_protected_context",
            )
        if len(risk_indicators) < 2 or not speaker_originated_evidence:
            return SharedActionResult(
                action="human_review",
                compatible=True,
                incompatibility_reason=None,
                speaker_originated_evidence=speaker_originated_evidence,
                risk_indicators=risk_indicators,
                protected_context=protected_context,
                rationale=rationale,
                adjustment="downgraded_insufficient_public_label_evidence",
            )
    return SharedActionResult(
        action=action,
        compatible=True,
        incompatibility_reason=None,
        speaker_originated_evidence=speaker_originated_evidence,
        risk_indicators=risk_indicators,
        protected_context=protected_context,
        rationale=rationale,
        adjustment=None,
    )


def normalize_hosted_output(raw_output: Any) -> SharedActionResult:
    """Strictly validate a hosted shared-action response without trusting it."""
    if not isinstance(raw_output, dict):
        return _incompatible("output must be a JSON object")
    expected = {
        "action",
        "speaker_originated_evidence",
        "risk_indicators",
        "protected_context",
        "rationale",
    }
    missing = sorted(expected - set(raw_output))
    if missing:
        return _incompatible(f"missing required fields: {', '.join(missing)}")
    action = raw_output["action"]
    if not isinstance(action, str) or action not in ACTIONS:
        return _incompatible("unsupported action")
    try:
        speaker = _string_list(raw_output["speaker_originated_evidence"], "speaker_originated_evidence")
        risk = _string_list(raw_output["risk_indicators"], "risk_indicators")
        protected = _string_list(raw_output["protected_context"], "protected_context")
    except SharedActionError as exc:
        return _incompatible(str(exc))
    unsupported_risk = sorted(set(risk) - PUBLIC_LABEL_RULES)
    if unsupported_risk:
        return _incompatible(f"unsupported risk_indicators: {', '.join(unsupported_risk)}")
    risk = list(dict.fromkeys(risk))
    unsupported_contexts = sorted(set(protected) - PROTECTED_CONTEXTS)
    if unsupported_contexts:
        return _incompatible(f"unsupported protected_context: {', '.join(unsupported_contexts)}")
    rationale = raw_output["rationale"]
    if not isinstance(rationale, str) or not rationale.strip():
        return _incompatible("rationale must be a non-empty string")
    return _apply_policy_guard(
        action=action,
        speaker_originated_evidence=speaker,
        risk_indicators=risk,
        protected_context=protected,
        rationale=rationale.strip(),
    )


def baseline_shared_action(text: str, score: float, thresholds: dict[str, float]) -> SharedActionResult:
    """Adapt the frozen local score surface, then apply the same policy guard."""
    evidence = policy_evidence(text)
    context = contextual_safety_evidence(text)
    matched_rules = [rule["name"] for rule in evidence["rules"] if rule["matched"]]
    risk = [rule for rule in matched_rules if rule in PUBLIC_LABEL_RULES]
    speaker = ["directed_reader_ask"] if context["directed_reader_ask"] else []
    protected: list[str] = []
    if context["protective_or_research_context"]:
        protected.append("warning")
    if context["satire_context"]:
        protected.append("satire")
    if context["developer_context"]:
        protected.append("debugging")
    if context["stance_aware_reportage"]:
        protected.append("reportage")
    native_action = (
        "public_label_candidate"
        if score >= float(thresholds["label"])
        else "human_review"
        if score >= float(thresholds["review"])
        else "no_action"
    )
    return _apply_policy_guard(
        action=native_action,
        speaker_originated_evidence=speaker,
        risk_indicators=risk,
        protected_context=protected,
        rationale="deterministic baseline adapter from frozen score thresholds and policy evidence",
    )


def load_fixture_replay(path: Path, rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Load fixture-only hosted records; never treat them as observed model output."""
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("mode") != "fixture_only_not_measured":
        raise SharedActionError("fixture must declare mode=fixture_only_not_measured")
    records = payload.get("records")
    if not isinstance(records, list) or not records:
        raise SharedActionError("fixture must contain at least one record")
    normalized = []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("caseIndex"), int):
            raise SharedActionError("fixture record requires integer caseIndex")
        case_index = record["caseIndex"]
        if case_index < 0 or case_index >= len(rows):
            raise SharedActionError("fixture caseIndex is outside the pinned test set")
        expected_hash = sha256(rows[case_index]["Post Content"].encode("utf-8"))
        if record.get("inputSha256") != expected_hash:
            raise SharedActionError(f"fixture input hash mismatch at caseIndex={case_index}")
        normalized.append(
            {
                "caseIndex": case_index,
                "inputSha256": expected_hash,
                "system": record.get("system", "fixture-hosted-system"),
                "result": normalize_hosted_output(record.get("rawOutput")),
            }
        )
    return normalized


def baseline_preflight(rows: list[dict[str, str]], model_path: Path) -> dict[str, Any]:
    register_pickle_compatibility()
    artifact = joblib.load(model_path)
    scores = artifact["model"].predict_proba([row["Post Content"] for row in rows])[:, 1]
    results = [
        baseline_shared_action(row["Post Content"], float(score), artifact["thresholds"])
        for row, score in zip(rows, scores)
    ]
    return {
        "status": "local_preflight_not_a_v2_comparison",
        "rows": len(results),
        "actionCounts": {action: sum(result.action == action for result in results) for action in sorted(ACTIONS)},
        "adjustmentCounts": {
            adjustment: sum(result.adjustment == adjustment for result in results)
            for adjustment in sorted({result.adjustment for result in results if result.adjustment})
        },
    }


def assert_v2_execution_blocked(approval_path: Path | None = None) -> None:
    """V2 is intentionally absent until a distinct reviewed approval exists."""
    if approval_path is None or not approval_path.is_file():
        raise PermissionError("V2 hosted execution blocked: reviewed current access/cost approval is absent")
    raise PermissionError("V2 hosted execution is not implemented in this offline milestone")
