import unittest

from policy_proposal_labeler_v2 import contextual_safety_evidence, decision_for_text, public_label_evidence


THRESHOLDS = {"review": 0.40, "label": 0.54, "high_confidence": 0.61}


class StanceAwarePolicyTest(unittest.TestCase):
    def test_skeptical_third_party_report_cannot_publicly_label(self):
        text = (
            "A service is offering guaranteed 18% returns, but I have not verified "
            "the license or official filings."
        )
        self.assertTrue(contextual_safety_evidence(text)["stance_aware_reportage"])
        self.assertFalse(public_label_evidence(text)["has_directed_reader_ask"])
        self.assertEqual(decision_for_text(text, 0.92, THRESHOLDS), "send_to_human_review")

    def test_reporting_frame_does_not_override_a_directed_ask(self):
        text = (
            "A service claims guaranteed returns, but I am unsure about it. "
            "Connect your wallet now to claim your bonus."
        )
        self.assertFalse(contextual_safety_evidence(text)["stance_aware_reportage"])
        self.assertTrue(public_label_evidence(text)["has_directed_reader_ask"])
        self.assertEqual(decision_for_text(text, 0.92, THRESHOLDS), "high_confidence_escalation")

    def test_direct_solicitation_remains_label_eligible(self):
        text = "Send 0.2 BTC to me today and receive a guaranteed double return."
        self.assertTrue(public_label_evidence(text)["has_public_label_evidence"])
        self.assertEqual(decision_for_text(text, 0.70, THRESHOLDS), "high_confidence_escalation")

    def test_identity_validation_transfer_is_a_directed_ask(self):
        text = (
            "Official Microsoft crypto grant for verified users. Send 0.05 BTC to "
            "validate identity and receive your bonus grant immediately."
        )
        self.assertTrue(public_label_evidence(text)["has_directed_reader_ask"])
        self.assertEqual(decision_for_text(text, 0.75, THRESHOLDS), "high_confidence_escalation")


if __name__ == "__main__":
    unittest.main()
