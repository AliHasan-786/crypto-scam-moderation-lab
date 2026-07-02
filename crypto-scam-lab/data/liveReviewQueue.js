export const liveReviewQueue = {
  "generatedAt": "2026-06-11T18:19:21.136382+00:00",
  "dbPath": "audit_outputs/live_review_queue.sqlite",
  "count": 5,
  "statusCounts": {
    "dismissed": 1,
    "escalated": 1,
    "new": 2,
    "review": 1
  },
  "items": [
    {
      "uri": "demo://crypto-scam-lab/high-confidence-airdrop",
      "cid": "demo-airdrop",
      "source": "demo",
      "sourceQuery": "seed-demo",
      "author": {
        "handle": "btc-rewards-demo.bsky.social",
        "did": "did:example:demo-airdrop",
        "displayName": null
      },
      "createdAt": "2026-06-07T00:00:00Z",
      "indexedAt": "2026-06-11T18:19:21.121682+00:00",
      "ingestedAt": "2026-06-07T14:52:15.658487+00:00",
      "updatedAt": "2026-06-11T18:19:21.128365+00:00",
      "text": "Official Bitcoin airdrop: connect your wallet at secure-btc-airdrop[.]xyz to claim free BTC before the window closes. Support wallet: 0x5afe00000000000000000000000000000000feed.",
      "probability": 0.8773451180253073,
      "action": "high_confidence_escalation",
      "thresholds": {
        "high_confidence": 0.61,
        "label": 0.5399999999999999,
        "review": 0.38999999999999996
      },
      "policyEvidence": {
        "digit_ratio": 0.192090395480226,
        "finance_term_count": 4,
        "label": "Potential Crypto Fraud",
        "rules": [
          {
            "contribution": 0.0,
            "description": "Guaranteed, risk-free, doubled, or implausibly high short-term gains.",
            "hits": 0,
            "matched": false,
            "name": "unrealistic_returns"
          },
          {
            "contribution": 0.23,
            "description": "Direct requests to send crypto, pay fees, deposit funds, or connect a wallet.",
            "hits": 1,
            "matched": true,
            "name": "crypto_transfer_request"
          },
          {
            "contribution": 0.19,
            "description": "Giveaways, airdrops, promo codes, free tokens, and prize/claim language.",
            "hits": 3,
            "matched": true,
            "name": "suspicious_giveaway"
          },
          {
            "contribution": 0.13,
            "description": "Official, verified, celebrity, exchange, or major-brand authority claims.",
            "hits": 1,
            "matched": true,
            "name": "authority_misuse"
          },
          {
            "contribution": 0.0,
            "description": "Time pressure, scarcity, or strong call-to-action phrasing.",
            "hits": 0,
            "matched": false,
            "name": "urgency_or_scarcity"
          },
          {
            "contribution": 0.0,
            "description": "Suspicious campaign domains, URL shorteners, or wallet-drainer-style links.",
            "hits": 0,
            "matched": false,
            "name": "risky_link_surface"
          }
        ],
        "score": 0.762,
        "uppercase_ratio": 0.03389830508474576,
        "walletish_string": true,
        "word_count": 19
      },
      "publicLabelEvidence": {
        "has_public_label_evidence": true,
        "matched_rules": [
          "crypto_transfer_request",
          "suspicious_giveaway",
          "authority_misuse"
        ],
        "public_label_rules": [
          "crypto_transfer_request",
          "suspicious_giveaway"
        ]
      },
      "contextualSafetyEvidence": {
        "developer_context": false,
        "protective_or_research_context": false,
        "public_label_suppressed": false,
        "review_preferred": false,
        "satire_context": false,
        "uncertain_review_context": false
      },
      "status": "escalated",
      "reviewerDecision": "fraud",
      "reviewerNotes": "Demo reviewer confirmed wallet-drainer-style airdrop evidence.",
      "reviewerId": "local-reviewer",
      "reviewedAt": "2026-06-07T14:52:28.176977+00:00",
      "duplicateCount": 2,
      "entities": [
        {
          "id": "e27ebc40f517bc83e17695d9",
          "type": "wallet",
          "value": "0x5afe00000000000000000000000000000000feed",
          "raw": "0x5afe00000000000000000000000000000000feed",
          "source": "ethereum_address",
          "riskWeight": 0.92,
          "observationCount": 2,
          "maxRiskWeight": 0.92
        },
        {
          "id": "369ad28ce164c1f46098ee17",
          "type": "risk_phrase",
          "value": "connect_wallet",
          "raw": "connect your wallet",
          "source": "policy_phrase",
          "riskWeight": 0.9,
          "observationCount": 2,
          "maxRiskWeight": 0.9
        },
        {
          "id": "6183f85ed949f6bc08d56067",
          "type": "risk_phrase",
          "value": "airdrop_claim",
          "raw": "airdrop",
          "source": "policy_phrase",
          "riskWeight": 0.76,
          "observationCount": 2,
          "maxRiskWeight": 0.76
        },
        {
          "id": "7e33162b472be211f94218cc",
          "type": "risk_phrase",
          "value": "limited_time",
          "raw": "window closes",
          "source": "policy_phrase",
          "riskWeight": 0.68,
          "observationCount": 2,
          "maxRiskWeight": 0.68
        },
        {
          "id": "ad2942dc24e97c86e747490c",
          "type": "domain",
          "value": "secure-btc-airdrop.xyz",
          "raw": "secure-btc-airdrop.xyz",
          "source": "text",
          "riskWeight": 0.58,
          "observationCount": 2,
          "maxRiskWeight": 0.58
        },
        {
          "id": "ee391cceed6698d8184b2a69",
          "type": "actor",
          "value": "btc-rewards-demo.bsky.social",
          "raw": "btc-rewards-demo.bsky.social",
          "source": "author_handle",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        },
        {
          "id": "3bfdcec1c5cbb3b8f884b614",
          "type": "actor",
          "value": "did:example:demo-airdrop",
          "raw": "did:example:demo-airdrop",
          "source": "author_did",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        },
        {
          "id": "75c0403b7442935ccd8c7889",
          "type": "brand",
          "value": "bitcoin",
          "raw": "Bitcoin",
          "source": "brand_mention",
          "riskWeight": 0.18,
          "observationCount": 2,
          "maxRiskWeight": 0.18
        }
      ]
    },
    {
      "uri": "demo://crypto-scam-lab/reused-wallet",
      "cid": "demo-reused-wallet",
      "source": "demo",
      "sourceQuery": "seed-demo",
      "author": {
        "handle": "token-support-demo.bsky.social",
        "did": "did:example:demo-reused-wallet",
        "displayName": null
      },
      "createdAt": "2026-06-07T00:06:00Z",
      "indexedAt": "2026-06-11T18:19:21.124067+00:00",
      "ingestedAt": "2026-06-11T18:19:21.132002+00:00",
      "updatedAt": "2026-06-11T18:19:21.132002+00:00",
      "text": "Tesla crypto event support says deposits to 0x5afe00000000000000000000000000000000feed are required before the bonus release fee clears.",
      "probability": 0.7593006830592476,
      "action": "high_confidence_escalation",
      "thresholds": {
        "high_confidence": 0.61,
        "label": 0.5399999999999999,
        "review": 0.38999999999999996
      },
      "policyEvidence": {
        "digit_ratio": 0.25,
        "finance_term_count": 1,
        "label": "Potential Crypto Fraud",
        "rules": [
          {
            "contribution": 0.0,
            "description": "Guaranteed, risk-free, doubled, or implausibly high short-term gains.",
            "hits": 0,
            "matched": false,
            "name": "unrealistic_returns"
          },
          {
            "contribution": 0.23,
            "description": "Direct requests to send crypto, pay fees, deposit funds, or connect a wallet.",
            "hits": 1,
            "matched": true,
            "name": "crypto_transfer_request"
          },
          {
            "contribution": 0.19,
            "description": "Giveaways, airdrops, promo codes, free tokens, and prize/claim language.",
            "hits": 1,
            "matched": true,
            "name": "suspicious_giveaway"
          },
          {
            "contribution": 0.13,
            "description": "Official, verified, celebrity, exchange, or major-brand authority claims.",
            "hits": 1,
            "matched": true,
            "name": "authority_misuse"
          },
          {
            "contribution": 0.0,
            "description": "Time pressure, scarcity, or strong call-to-action phrasing.",
            "hits": 0,
            "matched": false,
            "name": "urgency_or_scarcity"
          },
          {
            "contribution": 0.0,
            "description": "Suspicious campaign domains, URL shorteners, or wallet-drainer-style links.",
            "hits": 0,
            "matched": false,
            "name": "risky_link_surface"
          }
        ],
        "score": 0.7080000000000001,
        "uppercase_ratio": 0.007352941176470588,
        "walletish_string": true,
        "word_count": 16
      },
      "publicLabelEvidence": {
        "has_public_label_evidence": true,
        "matched_rules": [
          "crypto_transfer_request",
          "suspicious_giveaway",
          "authority_misuse"
        ],
        "public_label_rules": [
          "crypto_transfer_request",
          "suspicious_giveaway"
        ]
      },
      "contextualSafetyEvidence": {
        "developer_context": false,
        "protective_or_research_context": false,
        "public_label_suppressed": false,
        "review_preferred": false,
        "satire_context": false,
        "uncertain_review_context": false
      },
      "status": "new",
      "reviewerDecision": null,
      "reviewerNotes": null,
      "reviewerId": null,
      "reviewedAt": null,
      "duplicateCount": 1,
      "entities": [
        {
          "id": "e27ebc40f517bc83e17695d9",
          "type": "wallet",
          "value": "0x5afe00000000000000000000000000000000feed",
          "raw": "0x5afe00000000000000000000000000000000feed",
          "source": "ethereum_address",
          "riskWeight": 0.92,
          "observationCount": 2,
          "maxRiskWeight": 0.92
        },
        {
          "id": "a9ddee36ebaab1bcd241adb8",
          "type": "risk_phrase",
          "value": "processing_fee",
          "raw": "release fee",
          "source": "policy_phrase",
          "riskWeight": 0.74,
          "observationCount": 1,
          "maxRiskWeight": 0.74
        },
        {
          "id": "fa8489c9d014e11deefc0009",
          "type": "actor",
          "value": "did:example:demo-reused-wallet",
          "raw": "did:example:demo-reused-wallet",
          "source": "author_did",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        },
        {
          "id": "39710b7285f7126df391b097",
          "type": "actor",
          "value": "token-support-demo.bsky.social",
          "raw": "token-support-demo.bsky.social",
          "source": "author_handle",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        },
        {
          "id": "2a1377dd37e800133e318831",
          "type": "brand",
          "value": "tesla",
          "raw": "Tesla",
          "source": "brand_mention",
          "riskWeight": 0.18,
          "observationCount": 1,
          "maxRiskWeight": 0.18
        }
      ]
    },
    {
      "uri": "demo://crypto-scam-lab/consumer-warning",
      "cid": "demo-warning",
      "source": "demo",
      "sourceQuery": "seed-demo",
      "author": {
        "handle": "consumer-safety-demo.bsky.social",
        "did": "did:example:demo-warning",
        "displayName": null
      },
      "createdAt": "2026-06-07T00:00:00Z",
      "indexedAt": "2026-06-11T18:19:21.126144+00:00",
      "ingestedAt": "2026-06-07T14:52:15.663051+00:00",
      "updatedAt": "2026-06-11T18:19:21.133858+00:00",
      "text": "Reminder: do not send crypto to people promising guaranteed returns. Social media investment scams are common.",
      "probability": 0.7466655020447197,
      "action": "no_label",
      "thresholds": {
        "high_confidence": 0.61,
        "label": 0.5399999999999999,
        "review": 0.38999999999999996
      },
      "policyEvidence": {
        "digit_ratio": 0.0,
        "finance_term_count": 3,
        "label": "Potential Crypto Fraud",
        "rules": [
          {
            "contribution": 0.24,
            "description": "Guaranteed, risk-free, doubled, or implausibly high short-term gains.",
            "hits": 2,
            "matched": true,
            "name": "unrealistic_returns"
          },
          {
            "contribution": 0.23,
            "description": "Direct requests to send crypto, pay fees, deposit funds, or connect a wallet.",
            "hits": 1,
            "matched": true,
            "name": "crypto_transfer_request"
          },
          {
            "contribution": 0.0,
            "description": "Giveaways, airdrops, promo codes, free tokens, and prize/claim language.",
            "hits": 0,
            "matched": false,
            "name": "suspicious_giveaway"
          },
          {
            "contribution": 0.0,
            "description": "Official, verified, celebrity, exchange, or major-brand authority claims.",
            "hits": 0,
            "matched": false,
            "name": "authority_misuse"
          },
          {
            "contribution": 0.0,
            "description": "Time pressure, scarcity, or strong call-to-action phrasing.",
            "hits": 0,
            "matched": false,
            "name": "urgency_or_scarcity"
          },
          {
            "contribution": 0.0,
            "description": "Suspicious campaign domains, URL shorteners, or wallet-drainer-style links.",
            "hits": 0,
            "matched": false,
            "name": "risky_link_surface"
          }
        ],
        "score": 0.5840000000000001,
        "uppercase_ratio": 0.01818181818181818,
        "walletish_string": false,
        "word_count": 16
      },
      "publicLabelEvidence": {
        "has_public_label_evidence": true,
        "matched_rules": [
          "unrealistic_returns",
          "crypto_transfer_request"
        ],
        "public_label_rules": [
          "unrealistic_returns",
          "crypto_transfer_request"
        ]
      },
      "contextualSafetyEvidence": {
        "developer_context": false,
        "protective_or_research_context": true,
        "public_label_suppressed": true,
        "review_preferred": false,
        "satire_context": false,
        "uncertain_review_context": false
      },
      "status": "dismissed",
      "reviewerDecision": "not_fraud",
      "reviewerNotes": "Educational warning; no public label.",
      "reviewerId": "local-reviewer",
      "reviewedAt": "2026-06-07T14:52:28.176972+00:00",
      "duplicateCount": 2,
      "entities": [
        {
          "id": "3be5b9e417af4da7528c1b08",
          "type": "risk_phrase",
          "value": "send_crypto",
          "raw": "send crypto",
          "source": "policy_phrase",
          "riskWeight": 0.82,
          "observationCount": 1,
          "maxRiskWeight": 0.82
        },
        {
          "id": "fbc8ae918612c81c123a2994",
          "type": "risk_phrase",
          "value": "guaranteed_returns",
          "raw": "guaranteed returns",
          "source": "policy_phrase",
          "riskWeight": 0.78,
          "observationCount": 1,
          "maxRiskWeight": 0.78
        },
        {
          "id": "6f28125cb8baae11efbe6279",
          "type": "actor",
          "value": "consumer-safety-demo.bsky.social",
          "raw": "consumer-safety-demo.bsky.social",
          "source": "author_handle",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        },
        {
          "id": "856497870d9009de12365b9e",
          "type": "actor",
          "value": "did:example:demo-warning",
          "raw": "did:example:demo-warning",
          "source": "author_did",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        }
      ]
    },
    {
      "uri": "demo://crypto-scam-lab/mirror-airdrop",
      "cid": "demo-mirror-airdrop",
      "source": "demo",
      "sourceQuery": "seed-demo",
      "author": {
        "handle": "btc-claims-demo.bsky.social",
        "did": "did:example:demo-mirror-airdrop",
        "displayName": null
      },
      "createdAt": "2026-06-07T00:03:00Z",
      "indexedAt": "2026-06-11T18:19:21.122961+00:00",
      "ingestedAt": "2026-06-11T18:19:21.130980+00:00",
      "updatedAt": "2026-06-11T18:19:21.130980+00:00",
      "text": "Verified BTC rewards round is closing. Claim at secure-btc-airdrop[.]xyz and connect wallet before the final warning.",
      "probability": 0.6254492944325228,
      "action": "high_confidence_escalation",
      "thresholds": {
        "high_confidence": 0.61,
        "label": 0.5399999999999999,
        "review": 0.38999999999999996
      },
      "policyEvidence": {
        "digit_ratio": 0.0,
        "finance_term_count": 3,
        "label": "Potential Crypto Fraud",
        "rules": [
          {
            "contribution": 0.0,
            "description": "Guaranteed, risk-free, doubled, or implausibly high short-term gains.",
            "hits": 0,
            "matched": false,
            "name": "unrealistic_returns"
          },
          {
            "contribution": 0.0,
            "description": "Direct requests to send crypto, pay fees, deposit funds, or connect a wallet.",
            "hits": 0,
            "matched": false,
            "name": "crypto_transfer_request"
          },
          {
            "contribution": 0.19,
            "description": "Giveaways, airdrops, promo codes, free tokens, and prize/claim language.",
            "hits": 2,
            "matched": true,
            "name": "suspicious_giveaway"
          },
          {
            "contribution": 0.13,
            "description": "Official, verified, celebrity, exchange, or major-brand authority claims.",
            "hits": 1,
            "matched": true,
            "name": "authority_misuse"
          },
          {
            "contribution": 0.0,
            "description": "Time pressure, scarcity, or strong call-to-action phrasing.",
            "hits": 0,
            "matched": false,
            "name": "urgency_or_scarcity"
          },
          {
            "contribution": 0.0,
            "description": "Suspicious campaign domains, URL shorteners, or wallet-drainer-style links.",
            "hits": 0,
            "matched": false,
            "name": "risky_link_surface"
          }
        ],
        "score": 0.434,
        "uppercase_ratio": 0.042735042735042736,
        "walletish_string": false,
        "word_count": 16
      },
      "publicLabelEvidence": {
        "has_public_label_evidence": true,
        "matched_rules": [
          "suspicious_giveaway",
          "authority_misuse"
        ],
        "public_label_rules": [
          "suspicious_giveaway"
        ]
      },
      "contextualSafetyEvidence": {
        "developer_context": false,
        "protective_or_research_context": false,
        "public_label_suppressed": false,
        "review_preferred": false,
        "satire_context": false,
        "uncertain_review_context": false
      },
      "status": "new",
      "reviewerDecision": null,
      "reviewerNotes": null,
      "reviewerId": null,
      "reviewedAt": null,
      "duplicateCount": 1,
      "entities": [
        {
          "id": "369ad28ce164c1f46098ee17",
          "type": "risk_phrase",
          "value": "connect_wallet",
          "raw": "connect wallet",
          "source": "policy_phrase",
          "riskWeight": 0.9,
          "observationCount": 2,
          "maxRiskWeight": 0.9
        },
        {
          "id": "6183f85ed949f6bc08d56067",
          "type": "risk_phrase",
          "value": "airdrop_claim",
          "raw": "airdrop",
          "source": "policy_phrase",
          "riskWeight": 0.76,
          "observationCount": 2,
          "maxRiskWeight": 0.76
        },
        {
          "id": "7e33162b472be211f94218cc",
          "type": "risk_phrase",
          "value": "limited_time",
          "raw": "final warning",
          "source": "policy_phrase",
          "riskWeight": 0.68,
          "observationCount": 2,
          "maxRiskWeight": 0.68
        },
        {
          "id": "ad2942dc24e97c86e747490c",
          "type": "domain",
          "value": "secure-btc-airdrop.xyz",
          "raw": "secure-btc-airdrop.xyz",
          "source": "text",
          "riskWeight": 0.58,
          "observationCount": 2,
          "maxRiskWeight": 0.58
        },
        {
          "id": "f5e5f92f4e6cf1ef93198f36",
          "type": "actor",
          "value": "btc-claims-demo.bsky.social",
          "raw": "btc-claims-demo.bsky.social",
          "source": "author_handle",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        },
        {
          "id": "d8521c64e38ccb525c16c153",
          "type": "actor",
          "value": "did:example:demo-mirror-airdrop",
          "raw": "did:example:demo-mirror-airdrop",
          "source": "author_did",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        },
        {
          "id": "75c0403b7442935ccd8c7889",
          "type": "brand",
          "value": "bitcoin",
          "raw": "BTC",
          "source": "brand_mention",
          "riskWeight": 0.18,
          "observationCount": 2,
          "maxRiskWeight": 0.18
        }
      ]
    },
    {
      "uri": "demo://crypto-scam-lab/recovery-review",
      "cid": "demo-recovery",
      "source": "demo",
      "sourceQuery": "seed-demo",
      "author": {
        "handle": "wallet-help-demo.bsky.social",
        "did": "did:example:demo-recovery",
        "displayName": null
      },
      "createdAt": "2026-06-07T00:00:00Z",
      "indexedAt": "2026-06-11T18:19:21.125056+00:00",
      "ingestedAt": "2026-06-07T14:52:15.661438+00:00",
      "updatedAt": "2026-06-11T18:19:21.132776+00:00",
      "text": "A recovery service says they charge only after funds are recovered. Has anyone used them safely?",
      "probability": 0.2578952227200186,
      "action": "send_to_human_review",
      "thresholds": {
        "high_confidence": 0.61,
        "label": 0.5399999999999999,
        "review": 0.38999999999999996
      },
      "policyEvidence": {
        "digit_ratio": 0.0,
        "finance_term_count": 0,
        "label": "Potential Crypto Fraud",
        "rules": [
          {
            "contribution": 0.0,
            "description": "Guaranteed, risk-free, doubled, or implausibly high short-term gains.",
            "hits": 0,
            "matched": false,
            "name": "unrealistic_returns"
          },
          {
            "contribution": 0.0,
            "description": "Direct requests to send crypto, pay fees, deposit funds, or connect a wallet.",
            "hits": 0,
            "matched": false,
            "name": "crypto_transfer_request"
          },
          {
            "contribution": 0.0,
            "description": "Giveaways, airdrops, promo codes, free tokens, and prize/claim language.",
            "hits": 0,
            "matched": false,
            "name": "suspicious_giveaway"
          },
          {
            "contribution": 0.0,
            "description": "Official, verified, celebrity, exchange, or major-brand authority claims.",
            "hits": 0,
            "matched": false,
            "name": "authority_misuse"
          },
          {
            "contribution": 0.0,
            "description": "Time pressure, scarcity, or strong call-to-action phrasing.",
            "hits": 0,
            "matched": false,
            "name": "urgency_or_scarcity"
          },
          {
            "contribution": 0.0,
            "description": "Suspicious campaign domains, URL shorteners, or wallet-drainer-style links.",
            "hits": 0,
            "matched": false,
            "name": "risky_link_surface"
          }
        ],
        "score": 0.06,
        "uppercase_ratio": 0.020833333333333332,
        "walletish_string": false,
        "word_count": 16
      },
      "publicLabelEvidence": {
        "has_public_label_evidence": false,
        "matched_rules": [],
        "public_label_rules": []
      },
      "contextualSafetyEvidence": {
        "developer_context": false,
        "protective_or_research_context": false,
        "public_label_suppressed": false,
        "review_preferred": true,
        "satire_context": false,
        "uncertain_review_context": true
      },
      "status": "review",
      "reviewerDecision": "needs_more_context",
      "reviewerNotes": "Recovery-service context is risky but needs human review before public enforcement.",
      "reviewerId": "local-reviewer",
      "reviewedAt": "2026-06-07T14:52:28.176983+00:00",
      "duplicateCount": 2,
      "entities": [
        {
          "id": "a55696623c7d4a908a76e143",
          "type": "risk_phrase",
          "value": "recovery_service",
          "raw": "recovery service",
          "source": "policy_phrase",
          "riskWeight": 0.7,
          "observationCount": 1,
          "maxRiskWeight": 0.7
        },
        {
          "id": "c2a1f5fc7e1c51e59d98896f",
          "type": "actor",
          "value": "did:example:demo-recovery",
          "raw": "did:example:demo-recovery",
          "source": "author_did",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        },
        {
          "id": "88a656b5ca59db20a836b017",
          "type": "actor",
          "value": "wallet-help-demo.bsky.social",
          "raw": "wallet-help-demo.bsky.social",
          "source": "author_handle",
          "riskWeight": 0.2,
          "observationCount": 1,
          "maxRiskWeight": 0.2
        }
      ]
    }
  ]
};
