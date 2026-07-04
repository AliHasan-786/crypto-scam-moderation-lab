export const qualityCalibration = {
  "generatedAt": "2026-07-04T01:35:15.779902+00:00",
  "caseCount": 12,
  "coverage": {
    "publicLabelCases": 5,
    "humanReviewCases": 3,
    "noLabelCases": 4,
    "multilingualCases": 2,
    "urlOrRedirectCases": 4,
    "protectedContextCases": 7
  },
  "actionCounts": {
    "public_label": 5,
    "no_label": 4,
    "human_review": 3
  },
  "severityCounts": {
    "high": 5,
    "low": 4,
    "medium": 3
  },
  "policyFocusCounts": {
    "wallet_drainer": 1,
    "recovery_scam": 1,
    "consumer_warning": 1,
    "market_news": 1,
    "multilingual_wallet_drainer": 1,
    "multilingual_help_seeking": 1,
    "support_impersonation": 1,
    "developer_context": 1,
    "ocr_source_ambiguity": 1,
    "shortener_giveaway": 1,
    "satire": 1,
    "redirect_mismatch": 1
  },
  "calibrationStandards": [
    "Reviewer must cite concrete evidence for public labels.",
    "Reviewer must identify protected context before applying public labels.",
    "Suspicious but incomplete cases should route to human review.",
    "Reviewer notes should be specific enough for appeal and QA review.",
    "Repeated calibration misses should become policy guidance or eval cases."
  ],
  "recommendedQAProcess": [
    "Run calibration before reviewer launch and after policy updates.",
    "Score each reviewer against expected action, evidence quality, and context sensitivity.",
    "Review disagreement cases in group calibration.",
    "Promote common misses into evals and training examples.",
    "Track false-positive and false-negative themes over time."
  ],
  "sampleCases": [
    {
      "id": "calib_clear_wallet_drainer",
      "text": "Final airdrop window. Connect your wallet at secure-eth-airdrop.xyz and claim 5 ETH before eligibility expires.",
      "expected_action": "public_label",
      "expected_decision": "fraud",
      "policy_focus": "wallet_drainer",
      "severity": "high",
      "rationale": "Airdrop lure, wallet connection request, suspicious domain, and urgency justify a public Potential Crypto Fraud label."
    },
    {
      "id": "calib_recovery_fee",
      "text": "Lost crypto? Our verified recovery team can restore any wallet. Pay the processing fee in BTC upfront and your funds unlock today.",
      "expected_action": "public_label",
      "expected_decision": "fraud",
      "policy_focus": "recovery_scam",
      "severity": "high",
      "rationale": "Recovery service plus upfront crypto fee and certainty claims are classic fraud indicators."
    },
    {
      "id": "calib_consumer_warning",
      "text": "Fraud warning: do not send BTC to people promising guaranteed returns, and never connect your wallet to random airdrop links.",
      "expected_action": "no_label",
      "expected_decision": "not_fraud",
      "policy_focus": "consumer_warning",
      "severity": "low",
      "rationale": "The post discusses scam indicators in a protective warning context and should not be labeled as promotion."
    },
    {
      "id": "calib_market_news",
      "text": "Uniswap governance is discussing a possible airdrop for past users. No claim page is live and I am not sharing a wallet link.",
      "expected_action": "no_label",
      "expected_decision": "not_fraud",
      "policy_focus": "market_news",
      "severity": "low",
      "rationale": "Market/governance commentary with explicit no-link/no-claim context should suppress public enforcement."
    },
    {
      "id": "calib_spanish_wallet_lure",
      "text": "Airdrop oficial: conecta tu wallet en metamask-bono.top para reclamar ETH gratis. Ultima oportunidad.",
      "expected_action": "public_label",
      "expected_decision": "fraud",
      "policy_focus": "multilingual_wallet_drainer",
      "severity": "high",
      "rationale": "Spanish-language wallet-connection lure with suspicious brand/domain and urgency should be handled consistently."
    },
    {
      "id": "calib_spanish_help_seeking",
      "text": "Un grupo dice que puedo reclamar un airdrop si conecto mi billetera. No he verificado el enlace. Alguien sabe si es legitimo?",
      "expected_action": "human_review",
      "expected_decision": "needs_more_context",
      "policy_focus": "multilingual_help_seeking",
      "severity": "medium",
      "rationale": "Suspicious details are present, but the speaker appears to be asking for help rather than promoting the link."
    }
  ]
};
