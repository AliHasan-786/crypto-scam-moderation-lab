export const liveStreamCalibration = {
  "generatedAt": "2026-07-11 22:34Z",
  "source": "Bluesky Jetstream public firehose (app.bsky.feed.post creates)",
  "privacy": "Aggregates only. Post text was scored in memory and discarded; no text, handle, DID, URI, or per-post record was persisted.",
  "window": {
    "seconds": 240.0,
    "postsObserved": 11353,
    "postsScored": 8210,
    "scoredLanguages": [
      "en",
      "es"
    ],
    "skippedOtherLanguages": 3143,
    "languageMixTop": {
      "en": 7904,
      "und": 1029,
      "ja": 572,
      "pt": 449,
      "de": 314,
      "es": 306,
      "fr": 167,
      "ne": 140
    }
  },
  "thresholds": {
    "review": 0.4,
    "label": 0.5399999999999999,
    "high_confidence": 0.61
  },
  "decisionTierShares": {
    "no_label": {
      "count": 7610,
      "share": 0.9269
    },
    "send_to_human_review": {
      "count": 583,
      "share": 0.071
    },
    "apply_potential_crypto_fraud_label": {
      "count": 14,
      "share": 0.0017
    },
    "high_confidence_escalation": {
      "count": 3,
      "share": 0.0004
    }
  },
  "modelScore": {
    "mean": 0.3258,
    "p50": 0.3222,
    "p90": 0.3875,
    "p99": 0.4716,
    "histogram": [
      {
        "bin": "0.0-0.1",
        "count": 0,
        "share": 0.0
      },
      {
        "bin": "0.1-0.2",
        "count": 13,
        "share": 0.0016
      },
      {
        "bin": "0.2-0.3",
        "count": 2413,
        "share": 0.2939
      },
      {
        "bin": "0.3-0.4",
        "count": 5187,
        "share": 0.6318
      },
      {
        "bin": "0.4-0.5",
        "count": 552,
        "share": 0.0672
      },
      {
        "bin": "0.5-0.6",
        "count": 41,
        "share": 0.005
      },
      {
        "bin": "0.6-0.7",
        "count": 4,
        "share": 0.0005
      },
      {
        "bin": "0.7-0.8",
        "count": 0,
        "share": 0.0
      },
      {
        "bin": "0.8-0.9",
        "count": 0,
        "share": 0.0
      },
      {
        "bin": "0.9-1.0",
        "count": 0,
        "share": 0.0
      }
    ]
  },
  "policyScore": {
    "mean": 0.0733,
    "p99": 0.3,
    "histogram": [
      {
        "bin": "0.0-0.1",
        "count": 7774,
        "share": 0.9469
      },
      {
        "bin": "0.1-0.2",
        "count": 282,
        "share": 0.0343
      },
      {
        "bin": "0.2-0.3",
        "count": 54,
        "share": 0.0066
      },
      {
        "bin": "0.3-0.4",
        "count": 89,
        "share": 0.0108
      },
      {
        "bin": "0.4-0.5",
        "count": 10,
        "share": 0.0012
      },
      {
        "bin": "0.5-0.6",
        "count": 1,
        "share": 0.0001
      },
      {
        "bin": "0.6-0.7",
        "count": 0,
        "share": 0.0
      },
      {
        "bin": "0.7-0.8",
        "count": 0,
        "share": 0.0
      },
      {
        "bin": "0.8-0.9",
        "count": 0,
        "share": 0.0
      },
      {
        "bin": "0.9-1.0",
        "count": 0,
        "share": 0.0
      }
    ]
  },
  "topMatchedRules": {
    "risky_link_surface": 198,
    "unrealistic_returns": 93,
    "authority_misuse": 60,
    "suspicious_giveaway": 42,
    "urgency_or_scarcity": 41,
    "crypto_transfer_request": 2
  },
  "interpretation": "Real-traffic queue load at the shipped thresholds. The review-tier share here is measured on live posts, replacing the synthetic flagged-share assumption in the scale simulation. Tier shares are queue load, not prevalence: prevalence on real traffic requires labeled random sampling."
};
