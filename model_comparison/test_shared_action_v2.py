import tempfile
import unittest
from pathlib import Path

from model_comparison.shared_action_v2 import (
    ROOT,
    assert_v2_execution_blocked,
    baseline_shared_action,
    load_fixture_replay,
    load_pinned_test_rows,
    normalize_hosted_output,
)


class SharedActionV2Tests(unittest.TestCase):
    def test_valid_public_label_candidate_survives_shared_guard(self):
        result = normalize_hosted_output(
            {
                "action": "public_label_candidate",
                "speaker_originated_evidence": ["send BTC to my wallet"],
                "risk_indicators": ["crypto_transfer_request", "urgency_or_scarcity"],
                "protected_context": [],
                "rationale": "direct solicitation",
            }
        )
        self.assertTrue(result.compatible)
        self.assertEqual(result.action, "public_label_candidate")

    def test_protected_context_downgrades_public_label_candidate(self):
        result = normalize_hosted_output(
            {
                "action": "public_label_candidate",
                "speaker_originated_evidence": ["quoted offer"],
                "risk_indicators": ["unrealistic_returns", "crypto_transfer_request"],
                "protected_context": ["reportage"],
                "rationale": "skeptical report",
            }
        )
        self.assertTrue(result.compatible)
        self.assertEqual(result.action, "human_review")
        self.assertEqual(result.adjustment, "downgraded_protected_context")

    def test_invalid_output_is_incompatible_not_no_action(self):
        result = normalize_hosted_output(
            {
                "action": "block_now",
                "speaker_originated_evidence": [],
                "risk_indicators": [],
                "protected_context": [],
                "rationale": "bad action",
            }
        )
        self.assertFalse(result.compatible)
        self.assertIsNone(result.action)
        self.assertIn("unsupported", result.incompatibility_reason or "")

    def test_non_string_action_is_incompatible_not_an_exception(self):
        for action in ([], {}):
            result = normalize_hosted_output(
                {
                    "action": action,
                    "speaker_originated_evidence": [],
                    "risk_indicators": [],
                    "protected_context": [],
                    "rationale": "malformed action",
                }
            )
            self.assertFalse(result.compatible)
            self.assertIsNone(result.action)

    def test_unsupported_protected_context_is_incompatible(self):
        result = normalize_hosted_output(
            {
                "action": "no_action",
                "speaker_originated_evidence": [],
                "risk_indicators": [],
                "protected_context": ["commentary"],
                "rationale": "unsupported category",
            }
        )
        self.assertFalse(result.compatible)
        self.assertIsNone(result.action)
        self.assertIn("protected_context", result.incompatibility_reason or "")

    def test_unknown_risk_indicator_is_incompatible(self):
        result = normalize_hosted_output(
            {
                "action": "human_review",
                "speaker_originated_evidence": [],
                "risk_indicators": ["invented_category"],
                "protected_context": [],
                "rationale": "unknown risk",
            }
        )
        self.assertFalse(result.compatible)
        self.assertIn("risk_indicators", result.incompatibility_reason or "")

    def test_duplicate_risk_indicator_cannot_meet_public_label_requirement(self):
        result = normalize_hosted_output(
            {
                "action": "public_label_candidate",
                "speaker_originated_evidence": ["send to my wallet"],
                "risk_indicators": ["crypto_transfer_request", "crypto_transfer_request"],
                "protected_context": [],
                "rationale": "duplicate evidence",
            }
        )
        self.assertTrue(result.compatible)
        self.assertEqual(result.action, "human_review")
        self.assertEqual(result.adjustment, "downgraded_insufficient_public_label_evidence")

    def test_baseline_candidate_is_guarded_by_same_contract(self):
        result = baseline_shared_action(
            "A platform claims 20% returns, but I cannot verify it.",
            0.92,
            {"review": 0.4, "label": 0.54},
        )
        self.assertEqual(result.action, "human_review")
        self.assertEqual(result.adjustment, "downgraded_protected_context")

    def test_fixture_replay_is_hash_pinned_and_exposes_incompatibility(self):
        rows = load_pinned_test_rows(ROOT / "test.csv")
        records = load_fixture_replay(ROOT / "model_comparison/fixtures/v2_shared_action_replay.json", rows)
        self.assertEqual(len(records), 3)
        self.assertEqual(records[1]["result"].action, "human_review")
        self.assertFalse(records[2]["result"].compatible)

    def test_changed_input_is_rejected_before_fixture_or_baseline_replay(self):
        with tempfile.TemporaryDirectory() as directory:
            altered = Path(directory) / "test.csv"
            altered.write_bytes((ROOT / "test.csv").read_bytes() + b"\n")
            with self.assertRaisesRegex(Exception, "corpus hash"):
                load_pinned_test_rows(altered)

    def test_execution_remains_blocked_without_reviewed_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(PermissionError):
                assert_v2_execution_blocked(Path(directory) / "missing.json")


if __name__ == "__main__":
    unittest.main()
