export const hardeningSummary = {
  "generatedAt": "2026-07-04T02:15:54.947685+00:00",
  "caseCount": 12,
  "expectationPassRate": 1.0,
  "fraudPublicLabelRecall": 1.0,
  "reviewOrLabelRecall": 1.0,
  "legitimateNoPublicLabelRate": 1.0,
  "ambiguousReviewRate": 1.0,
  "canonicalizationAppliedCount": 9,
  "urlCaseCount": 7,
  "dimensionSummary": [
    {
      "name": "false_positive_control",
      "count": 4,
      "passed": 4,
      "passRate": 1.0,
      "publicLabels": 0,
      "reviewOrLabel": 0
    },
    {
      "name": "url_evidence",
      "count": 4,
      "passed": 4,
      "passRate": 1.0,
      "publicLabels": 2,
      "reviewOrLabel": 3
    },
    {
      "name": "defanged_url",
      "count": 3,
      "passed": 3,
      "passRate": 1.0,
      "publicLabels": 2,
      "reviewOrLabel": 2
    },
    {
      "name": "multilingual",
      "count": 3,
      "passed": 3,
      "passRate": 1.0,
      "publicLabels": 1,
      "reviewOrLabel": 2
    },
    {
      "name": "review_routing",
      "count": 3,
      "passed": 3,
      "passRate": 1.0,
      "publicLabels": 0,
      "reviewOrLabel": 3
    },
    {
      "name": "brand_impersonation",
      "count": 2,
      "passed": 2,
      "passRate": 1.0,
      "publicLabels": 2,
      "reviewOrLabel": 2
    },
    {
      "name": "canonicalization",
      "count": 2,
      "passed": 2,
      "passRate": 1.0,
      "publicLabels": 2,
      "reviewOrLabel": 2
    },
    {
      "name": "missing_context",
      "count": 2,
      "passed": 2,
      "passRate": 1.0,
      "publicLabels": 0,
      "reviewOrLabel": 2
    }
  ],
  "topUrlEvidence": [
    {
      "caseId": "hardening_spaced_wallet_defanged_airdrop",
      "domain": "secure-airdrop.xyz",
      "riskWeight": 0.62,
      "riskFactors": [
        "campaign_keyword_domain",
        "defanged_url",
        "suspicious_tld",
        "wallet_or_claim_path"
      ]
    },
    {
      "caseId": "hardening_defanged_research_warning",
      "domain": "secure-airdrop.xyz",
      "riskWeight": 0.62,
      "riskFactors": [
        "campaign_keyword_domain",
        "defanged_url",
        "suspicious_tld",
        "wallet_or_claim_path"
      ]
    },
    {
      "caseId": "hardening_spanish_wallet_airdrop",
      "domain": "metamask-bono.top",
      "riskWeight": 0.56,
      "riskFactors": [
        "brand_impersonation_domain",
        "defanged_url",
        "suspicious_tld"
      ]
    },
    {
      "caseId": "hardening_brand_impersonation_domain",
      "domain": "metamask-security.top",
      "riskWeight": 0.56,
      "riskFactors": [
        "brand_impersonation_domain",
        "defanged_url",
        "suspicious_tld"
      ]
    },
    {
      "caseId": "hardening_developer_wallet_debug",
      "domain": "dev-wallet.local",
      "riskWeight": 0.5,
      "riskFactors": [
        "campaign_keyword_domain",
        "defanged_url",
        "wallet_or_claim_path"
      ]
    }
  ],
  "topFailureIds": [],
  "examples": [
    {
      "caseId": "hardening_spaced_wallet_defanged_airdrop",
      "scenario": "canonicalization_spaced_keywords",
      "action": "high_confidence_escalation",
      "passed": true,
      "dimensions": [
        "canonicalization",
        "defanged_url",
        "wallet_drainer"
      ],
      "topUrlDomain": "secure-airdrop.xyz",
      "topUrlFactors": [
        "campaign_keyword_domain",
        "defanged_url",
        "suspicious_tld",
        "wallet_or_claim_path"
      ]
    },
    {
      "caseId": "hardening_leetspeak_support_deposit",
      "scenario": "canonicalization_leetspeak",
      "action": "apply_potential_crypto_fraud_label",
      "passed": true,
      "dimensions": [
        "canonicalization",
        "leetspeak",
        "support_impersonation"
      ],
      "topUrlDomain": "",
      "topUrlFactors": []
    },
    {
      "caseId": "hardening_spanish_wallet_airdrop",
      "scenario": "multilingual_spanish_fraud",
      "action": "high_confidence_escalation",
      "passed": true,
      "dimensions": [
        "multilingual",
        "defanged_url",
        "brand_impersonation"
      ],
      "topUrlDomain": "metamask-bono.top",
      "topUrlFactors": [
        "brand_impersonation_domain",
        "defanged_url",
        "suspicious_tld"
      ]
    },
    {
      "caseId": "hardening_shortener_claim_lure",
      "scenario": "url_shortener_claim",
      "action": "high_confidence_escalation",
      "passed": true,
      "dimensions": [
        "url_evidence",
        "shortener",
        "giveaway"
      ],
      "topUrlDomain": "bit.ly",
      "topUrlFactors": [
        "url_shortener",
        "wallet_or_claim_path"
      ]
    },
    {
      "caseId": "hardening_brand_impersonation_domain",
      "scenario": "brand_impersonation_domain",
      "action": "apply_potential_crypto_fraud_label",
      "passed": true,
      "dimensions": [
        "url_evidence",
        "brand_impersonation",
        "wallet_connection"
      ],
      "topUrlDomain": "metamask-security.top",
      "topUrlFactors": [
        "brand_impersonation_domain",
        "defanged_url",
        "suspicious_tld"
      ]
    },
    {
      "caseId": "hardening_ocr_cropped_qr_review",
      "scenario": "ocr_source_ambiguity",
      "action": "send_to_human_review",
      "passed": true,
      "dimensions": [
        "ocr",
        "missing_context",
        "review_routing"
      ],
      "topUrlDomain": "",
      "topUrlFactors": []
    }
  ]
};
