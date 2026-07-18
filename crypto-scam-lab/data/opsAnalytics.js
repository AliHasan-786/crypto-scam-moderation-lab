export const opsAnalytics = {
  "generatedAt": "2026-07-18T03:35:02.855899+00:00",
  "summary": {
    "totalItems": 5,
    "reviewedItems": 3,
    "unreviewedItems": 2,
    "actionedItems": 1,
    "dismissedItems": 1,
    "totalObservations": 8,
    "avgProbability": 0.6533,
    "reviewCoverage": 0.6,
    "backlogRate": 0.4,
    "actionRate": 0.2,
    "dismissalRateAmongReviewed": 0.3333
  },
  "statusCounts": [
    {
      "status": "new",
      "count": 2
    },
    {
      "status": "dismissed",
      "count": 1
    },
    {
      "status": "escalated",
      "count": 1
    },
    {
      "status": "review",
      "count": 1
    }
  ],
  "decisionCounts": [
    {
      "decision": "unreviewed",
      "count": 2
    },
    {
      "decision": "fraud",
      "count": 1
    },
    {
      "decision": "needs_more_context",
      "count": 1
    },
    {
      "decision": "not_fraud",
      "count": 1
    }
  ],
  "actionCounts": [
    {
      "action": "high_confidence_escalation",
      "count": 3,
      "avg_probability": 0.754
    },
    {
      "action": "no_label",
      "count": 1,
      "avg_probability": 0.7467
    },
    {
      "action": "send_to_human_review",
      "count": 1,
      "avg_probability": 0.2579
    }
  ],
  "topEntities": [
    {
      "entity_type": "wallet",
      "value": "0x5afe00000000000000000000000000000000feed",
      "observation_count": 2,
      "max_risk_weight": 0.92,
      "linked_items": 2
    },
    {
      "entity_type": "risk_phrase",
      "value": "connect_wallet",
      "observation_count": 2,
      "max_risk_weight": 0.9,
      "linked_items": 2
    },
    {
      "entity_type": "risk_phrase",
      "value": "airdrop_claim",
      "observation_count": 2,
      "max_risk_weight": 0.76,
      "linked_items": 2
    },
    {
      "entity_type": "risk_phrase",
      "value": "limited_time",
      "observation_count": 2,
      "max_risk_weight": 0.68,
      "linked_items": 2
    },
    {
      "entity_type": "domain",
      "value": "secure-btc-airdrop.xyz",
      "observation_count": 2,
      "max_risk_weight": 0.58,
      "linked_items": 2
    },
    {
      "entity_type": "brand",
      "value": "bitcoin",
      "observation_count": 2,
      "max_risk_weight": 0.18,
      "linked_items": 2
    }
  ],
  "backlogItems": [
    {
      "uri": "demo://crypto-scam-lab/reused-wallet",
      "author_handle": "token-support-demo.bsky.social",
      "probability": 0.7593,
      "action": "high_confidence_escalation",
      "status": "new",
      "duplicate_count": 1,
      "text_preview": "Tesla crypto event support says deposits to 0x5afe00000000000000000000000000000000feed are required before the bonus release fee clears."
    },
    {
      "uri": "demo://crypto-scam-lab/mirror-airdrop",
      "author_handle": "btc-claims-demo.bsky.social",
      "probability": 0.6254,
      "action": "high_confidence_escalation",
      "status": "new",
      "duplicate_count": 1,
      "text_preview": "Verified BTC rewards round is closing. Claim at secure-btc-airdrop[.]xyz and connect wallet before the final warning."
    }
  ],
  "falsePositiveCandidates": [
    {
      "uri": "demo://crypto-scam-lab/consumer-warning",
      "author_handle": "consumer-safety-demo.bsky.social",
      "probability": 0.7467,
      "action": "no_label",
      "status": "dismissed",
      "reviewer_decision": "not_fraud",
      "reviewer_notes": "Educational warning; no public label.",
      "text_preview": "Reminder: do not send crypto to people promising guaranteed returns. Social media investment scams are common."
    }
  ],
  "riskNotes": [
    "Backlog exists; prioritize unresolved items by action tier, probability, duplicate count, and shared entities.",
    "Dismissed/not-fraud cases should feed policy clarification and false-positive evals.",
    "Repeated entities are useful campaign leads, but should not trigger enforcement without content and context review.",
    "Reviewer decisions create an active-learning and QA feedback loop."
  ]
};
