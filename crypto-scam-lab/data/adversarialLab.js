export const adversarialLab = {
  "generatedAt": "2026-07-04T02:15:56.515050+00:00",
  "suite": "adversarial_scam_mutation_lab_v1",
  "seedCount": 7,
  "mutationCount": 8,
  "variantCount": 56,
  "publicLabelRetentionRate": 0.8214285714285714,
  "reviewOrLabelRetentionRate": 1.0,
  "downgradeRate": 0.25,
  "escapeRate": 0.0,
  "severeDowngradeRate": 0.0,
  "avgProbabilityDelta": -0.03510365361896651,
  "actionCounts": {
    "apply_potential_crypto_fraud_label": 7,
    "high_confidence_escalation": 39,
    "send_to_human_review": 10
  },
  "mutationSummary": [
    {
      "id": "screenshot_ocr",
      "label": "Screenshot OCR",
      "category": "multimodal_placeholder",
      "attackGoal": "Represent a scam as OCR from an image where source and link context are missing.",
      "standards": [
        "OWASP: multimodal content risk",
        "NIST AI RMF Map"
      ],
      "variantCount": 7,
      "publicLabelRetentionRate": 0.0,
      "reviewOrLabelRetentionRate": 1.0,
      "escapeCount": 0,
      "downgradeCount": 7,
      "severeDowngradeCount": 0,
      "avgProbabilityDelta": -0.0018187276333879096,
      "worstVariantId": "fraud_fake_exchange_support__screenshot_ocr",
      "worstAction": "send_to_human_review",
      "worstProbability": 0.6122643588954335
    },
    {
      "id": "synonym_laundering",
      "label": "Synonym laundering",
      "category": "semantic_obfuscation",
      "attackGoal": "Replace policy-trigger words with softer funnel language.",
      "standards": [
        "MITRE ATLAS: robustness testing",
        "NIST AI RMF Measure"
      ],
      "variantCount": 7,
      "publicLabelRetentionRate": 0.7142857142857143,
      "reviewOrLabelRetentionRate": 1.0,
      "escapeCount": 0,
      "downgradeCount": 3,
      "severeDowngradeCount": 0,
      "avgProbabilityDelta": -0.14876327623322605,
      "worstVariantId": "fraud_fake_exchange_support__synonym_laundering",
      "worstAction": "send_to_human_review",
      "worstProbability": 0.4535970994529193
    },
    {
      "id": "context_laundering",
      "label": "Context laundering",
      "category": "semantic_obfuscation",
      "attackGoal": "Wrap the scam ask in support/eligibility language.",
      "standards": [
        "Santa Clara Understandable Rules",
        "NIST AI RMF Manage"
      ],
      "variantCount": 7,
      "publicLabelRetentionRate": 0.8571428571428571,
      "reviewOrLabelRetentionRate": 1.0,
      "escapeCount": 0,
      "downgradeCount": 3,
      "severeDowngradeCount": 0,
      "avgProbabilityDelta": -0.12006108849561356,
      "worstVariantId": "fraud_fake_exchange_support__context_laundering",
      "worstAction": "send_to_human_review",
      "worstProbability": 0.47592220957585596
    },
    {
      "id": "leetspeak",
      "label": "Leetspeak",
      "category": "lexical_obfuscation",
      "attackGoal": "Substitute visually similar characters to test char n-gram robustness.",
      "standards": [
        "MITRE ATLAS: evasion testing",
        "NIST AI RMF Measure"
      ],
      "variantCount": 7,
      "publicLabelRetentionRate": 1.0,
      "reviewOrLabelRetentionRate": 1.0,
      "escapeCount": 0,
      "downgradeCount": 1,
      "severeDowngradeCount": 0,
      "avgProbabilityDelta": -0.03471626306364571,
      "worstVariantId": "fraud_recovery_fee_advance__leetspeak",
      "worstAction": "apply_potential_crypto_fraud_label",
      "worstProbability": 0.5941453138707402
    },
    {
      "id": "spaced_keywords",
      "label": "Spaced keywords",
      "category": "lexical_obfuscation",
      "attackGoal": "Break exact keyword and n-gram matches while preserving the scam ask.",
      "standards": [
        "MITRE ATLAS: evasion testing",
        "NIST AI RMF Measure"
      ],
      "variantCount": 7,
      "publicLabelRetentionRate": 1.0,
      "reviewOrLabelRetentionRate": 1.0,
      "escapeCount": 0,
      "downgradeCount": 0,
      "severeDowngradeCount": 0,
      "avgProbabilityDelta": -0.0033532359135676044,
      "worstVariantId": "fraud_fake_exchange_support__spaced_keywords",
      "worstAction": "high_confidence_escalation",
      "worstProbability": 0.6284212675616402
    },
    {
      "id": "punctuation_stuffing",
      "label": "Punctuation stuffing",
      "category": "lexical_obfuscation",
      "attackGoal": "Insert punctuation and spacing noise into enforcement-triggering terms.",
      "standards": [
        "MITRE ATLAS: evasion testing",
        "NIST CSF Detect"
      ],
      "variantCount": 7,
      "publicLabelRetentionRate": 1.0,
      "reviewOrLabelRetentionRate": 1.0,
      "escapeCount": 0,
      "downgradeCount": 0,
      "severeDowngradeCount": 0,
      "avgProbabilityDelta": -0.035574810687708416,
      "worstVariantId": "fraud_fake_exchange_support__punctuation_stuffing",
      "worstAction": "apply_potential_crypto_fraud_label",
      "worstProbability": 0.6030069437548354
    },
    {
      "id": "defanged_url",
      "label": "Defanged URL",
      "category": "link_obfuscation",
      "attackGoal": "Hide risky domains behind hxxp and bracket-dot notation.",
      "standards": [
        "OWASP: untrusted content handling",
        "NIST CSF Detect"
      ],
      "variantCount": 7,
      "publicLabelRetentionRate": 1.0,
      "reviewOrLabelRetentionRate": 1.0,
      "escapeCount": 0,
      "downgradeCount": 0,
      "severeDowngradeCount": 0,
      "avgProbabilityDelta": 0.05848624912736146,
      "worstVariantId": "fraud_fake_exchange_support__defanged_url",
      "worstAction": "high_confidence_escalation",
      "worstProbability": 0.7319034195543597
    },
    {
      "id": "brand_impersonation_shift",
      "label": "Brand shift",
      "category": "impersonation_variant",
      "attackGoal": "Move the same lure across brands or public entities.",
      "standards": [
        "Santa Clara Integrity",
        "NIST AI RMF Map"
      ],
      "variantCount": 7,
      "publicLabelRetentionRate": 1.0,
      "reviewOrLabelRetentionRate": 1.0,
      "escapeCount": 0,
      "downgradeCount": 0,
      "severeDowngradeCount": 0,
      "avgProbabilityDelta": 0.004971923948055711,
      "worstVariantId": "fraud_fake_exchange_support__brand_impersonation_shift",
      "worstAction": "apply_potential_crypto_fraud_label",
      "worstProbability": 0.6098460134298528
    }
  ],
  "categorySummary": {
    "impersonation_variant": {
      "variantCount": 7,
      "escapeCount": 0,
      "downgradeCount": 0,
      "reviewOrLabelRetentionRate": 1.0,
      "publicLabelRetentionRate": 1.0
    },
    "lexical_obfuscation": {
      "variantCount": 21,
      "escapeCount": 0,
      "downgradeCount": 1,
      "reviewOrLabelRetentionRate": 1.0,
      "publicLabelRetentionRate": 1.0
    },
    "link_obfuscation": {
      "variantCount": 7,
      "escapeCount": 0,
      "downgradeCount": 0,
      "reviewOrLabelRetentionRate": 1.0,
      "publicLabelRetentionRate": 1.0
    },
    "multimodal_placeholder": {
      "variantCount": 7,
      "escapeCount": 0,
      "downgradeCount": 7,
      "reviewOrLabelRetentionRate": 1.0,
      "publicLabelRetentionRate": 0.0
    },
    "semantic_obfuscation": {
      "variantCount": 14,
      "escapeCount": 0,
      "downgradeCount": 6,
      "reviewOrLabelRetentionRate": 1.0,
      "publicLabelRetentionRate": 0.7857142857142857
    }
  },
  "topWeaknesses": [
    {
      "id": "fraud_wallet_drainer_airdrop__synonym_laundering",
      "seedId": "fraud_wallet_drainer_airdrop",
      "mutationLabel": "Synonym laundering",
      "category": "semantic_obfuscation",
      "baselineAction": "high_confidence_escalation",
      "mutatedAction": "send_to_human_review",
      "baselineProbability": 0.8070956234308397,
      "mutatedProbability": 0.4703006772354069,
      "probabilityDelta": -0.3367949461954328,
      "publicLabelDropped": true,
      "escaped": false,
      "mutatedText": "Final allocation window is open. sync your vault at secure-eth-allocation.xyz now to redeem complimentary ETH before eligibility expires."
    },
    {
      "id": "fraud_recovery_fee_advance__screenshot_ocr",
      "seedId": "fraud_recovery_fee_advance",
      "mutationLabel": "Screenshot OCR",
      "category": "multimodal_placeholder",
      "baselineAction": "high_confidence_escalation",
      "mutatedAction": "send_to_human_review",
      "baselineProbability": 0.6570928219100404,
      "mutatedProbability": 0.662594294186746,
      "probabilityDelta": 0.00550147227670561,
      "publicLabelDropped": true,
      "escaped": false,
      "mutatedText": "[Image OCR]\nScreenshot text: Lost crypto? Our verified recovery team can restore any wallet. Pay the processing fee in BTC upfront and your funds unlock today.\nQR code visible. Link is partially cropped. Source account not visible."
    },
    {
      "id": "fraud_promo_code_fee__screenshot_ocr",
      "seedId": "fraud_promo_code_fee",
      "mutationLabel": "Screenshot OCR",
      "category": "multimodal_placeholder",
      "baselineAction": "high_confidence_escalation",
      "mutatedAction": "send_to_human_review",
      "baselineProbability": 0.6965428989293474,
      "mutatedProbability": 0.6921523085121176,
      "probabilityDelta": -0.004390590417229778,
      "publicLabelDropped": true,
      "escaped": false,
      "mutatedText": "[Image OCR]\nScreenshot text: Congratulations, your promo code unlocked 2 BTC. Send the small activation fee to the wallet address and claim your prize.\nQR code visible. Link is partially cropped. Source account not visible."
    },
    {
      "id": "fraud_fake_grant__screenshot_ocr",
      "seedId": "fraud_fake_grant",
      "mutationLabel": "Screenshot OCR",
      "category": "multimodal_placeholder",
      "baselineAction": "high_confidence_escalation",
      "mutatedAction": "send_to_human_review",
      "baselineProbability": 0.754939795765245,
      "mutatedProbability": 0.7542335832122881,
      "probabilityDelta": -0.0007062125529568863,
      "publicLabelDropped": true,
      "escaped": false,
      "mutatedText": "[Image OCR]\nScreenshot text: Official Microsoft crypto grant for verified users. Send 0.05 BTC to validate identity and receive your bonus grant immediately.\nQR code visible. Link is partially cropped. Source account not visible."
    },
    {
      "id": "fraud_wallet_drainer_airdrop__screenshot_ocr",
      "seedId": "fraud_wallet_drainer_airdrop",
      "mutationLabel": "Screenshot OCR",
      "category": "multimodal_placeholder",
      "baselineAction": "high_confidence_escalation",
      "mutatedAction": "send_to_human_review",
      "baselineProbability": 0.8070956234308397,
      "mutatedProbability": 0.8009397965426335,
      "probabilityDelta": -0.006155826888206262,
      "publicLabelDropped": true,
      "escaped": false,
      "mutatedText": "[Image OCR]\nScreenshot text: Final airdrop window is open. Connect your wallet at secure-eth-airdrop.xyz now to claim free ETH before eligibility expires.\nQR code visible. Link is partially cropped. Source account not visible."
    }
  ]
};
