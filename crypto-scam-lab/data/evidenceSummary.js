export const evidenceSummary = {
  "generatedAt": "2026-07-04T01:35:15.727560+00:00",
  "suite": "structured_evidence_extractor_v1",
  "provider": "deterministic_rubric_v1",
  "caseCount": 19,
  "passRate": 1.0,
  "spanFaithfulnessRate": 1.0,
  "fraudEvidenceRecall": 1.0,
  "legitimateNoPublicLabelRate": 1.0,
  "ambiguousReviewRate": 1.0,
  "actionCounts": {
    "human_review": 5,
    "no_action": 6,
    "public_label_candidate": 8
  },
  "failureCounts": {},
  "examples": [
    {
      "caseId": "fraud_elon_multiplier",
      "scenario": "celebrity_impersonation",
      "recommendedReviewerAction": "public_label_candidate",
      "confidence": 0.74,
      "riskFactors": [
        "promised_return",
        "transfer_ask",
        "impersonated_entity",
        "urgency"
      ],
      "benignFactors": [],
      "missingContext": [],
      "reviewerSummary": "Concrete scam evidence is present (promised_return, transfer_ask, impersonated_entity, urgency) with no benign-context field; this is a candidate for reviewer-confirmed public labeling."
    },
    {
      "caseId": "fraud_wallet_drainer_airdrop",
      "scenario": "wallet_drainer",
      "recommendedReviewerAction": "public_label_candidate",
      "confidence": 0.685,
      "riskFactors": [
        "wallet_connection_ask",
        "urgency",
        "risky_link_or_wallet"
      ],
      "benignFactors": [],
      "missingContext": [],
      "reviewerSummary": "Concrete scam evidence is present (wallet_connection_ask, urgency, risky_link_or_wallet) with no benign-context field; this is a candidate for reviewer-confirmed public labeling."
    },
    {
      "caseId": "fraud_recovery_fee_advance",
      "scenario": "recovery_scam",
      "recommendedReviewerAction": "public_label_candidate",
      "confidence": 0.685,
      "riskFactors": [
        "transfer_ask",
        "impersonated_entity",
        "recovery_claim"
      ],
      "benignFactors": [],
      "missingContext": [],
      "reviewerSummary": "Concrete scam evidence is present (transfer_ask, impersonated_entity, recovery_claim) with no benign-context field; this is a candidate for reviewer-confirmed public labeling."
    },
    {
      "caseId": "fraud_hyip_guaranteed_returns",
      "scenario": "investment_scam",
      "recommendedReviewerAction": "public_label_candidate",
      "confidence": 0.685,
      "riskFactors": [
        "promised_return",
        "transfer_ask",
        "urgency"
      ],
      "benignFactors": [],
      "missingContext": [],
      "reviewerSummary": "Concrete scam evidence is present (promised_return, transfer_ask, urgency) with no benign-context field; this is a candidate for reviewer-confirmed public labeling."
    },
    {
      "caseId": "fraud_fake_exchange_support",
      "scenario": "fake_support",
      "recommendedReviewerAction": "public_label_candidate",
      "confidence": 0.685,
      "riskFactors": [
        "transfer_ask",
        "wallet_connection_ask",
        "impersonated_entity"
      ],
      "benignFactors": [],
      "missingContext": [],
      "reviewerSummary": "Concrete scam evidence is present (transfer_ask, wallet_connection_ask, impersonated_entity) with no benign-context field; this is a candidate for reviewer-confirmed public labeling."
    },
    {
      "caseId": "fraud_promo_code_fee",
      "scenario": "giveaway_fee",
      "recommendedReviewerAction": "public_label_candidate",
      "confidence": 0.63,
      "riskFactors": [
        "transfer_ask",
        "wallet_connection_ask"
      ],
      "benignFactors": [],
      "missingContext": [],
      "reviewerSummary": "Concrete scam evidence is present (transfer_ask, wallet_connection_ask) with no benign-context field; this is a candidate for reviewer-confirmed public labeling."
    }
  ]
};
