# Adversarial Scam Lab Report

Generated: 2026-07-11T22:40:18.758200+00:00

## Summary

- Seed scam cases: 7
- Mutation operators: 8
- Mutated variants: 56
- Public-label retention: 82.1%
- Review-or-label retention: 100.0%
- Downgrade rate: 25.0%
- Escape rate: 0.0%
- Severe downgrade rate: 0.0%
- Average probability delta: -0.035

Interpretation: review-or-label retention is the recall-first safety metric. Public-label retention is stricter, because some adversarial posts may be better routed to human review before public enforcement.

## Mutation Results

| Mutation | Category | Variants | Public-label retained | Review/label retained | Escapes | Downgrades | Worst action |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| Screenshot OCR | multimodal_placeholder | 7 | 0.0% | 100.0% | 0 | 7 | send_to_human_review |
| Synonym laundering | semantic_obfuscation | 7 | 71.4% | 100.0% | 0 | 3 | send_to_human_review |
| Context laundering | semantic_obfuscation | 7 | 85.7% | 100.0% | 0 | 3 | send_to_human_review |
| Leetspeak | lexical_obfuscation | 7 | 100.0% | 100.0% | 0 | 1 | apply_potential_crypto_fraud_label |
| Spaced keywords | lexical_obfuscation | 7 | 100.0% | 100.0% | 0 | 0 | high_confidence_escalation |
| Punctuation stuffing | lexical_obfuscation | 7 | 100.0% | 100.0% | 0 | 0 | apply_potential_crypto_fraud_label |
| Defanged URL | link_obfuscation | 7 | 100.0% | 100.0% | 0 | 0 | high_confidence_escalation |
| Brand shift | impersonation_variant | 7 | 100.0% | 100.0% | 0 | 0 | apply_potential_crypto_fraud_label |

## Top Weaknesses

### fraud_wallet_drainer_airdrop__synonym_laundering

- Mutation: Synonym laundering
- Baseline action: high_confidence_escalation
- Mutated action: send_to_human_review
- Probability delta: -0.337
- Public label dropped: True
- Escaped review/label: False

```text
Final allocation window is open. sync your vault at secure-eth-allocation.xyz now to redeem complimentary ETH before eligibility expires.
```

### fraud_recovery_fee_advance__screenshot_ocr

- Mutation: Screenshot OCR
- Baseline action: high_confidence_escalation
- Mutated action: send_to_human_review
- Probability delta: 0.006
- Public label dropped: True
- Escaped review/label: False

```text
[Image OCR]
Screenshot text: Lost crypto? Our verified recovery team can restore any wallet. Pay the processing fee in BTC upfront and your funds unlock today.
QR code visible. Link is partially cropped. Source account not visible.
```

### fraud_promo_code_fee__screenshot_ocr

- Mutation: Screenshot OCR
- Baseline action: high_confidence_escalation
- Mutated action: send_to_human_review
- Probability delta: -0.004
- Public label dropped: True
- Escaped review/label: False

```text
[Image OCR]
Screenshot text: Congratulations, your promo code unlocked 2 BTC. Send the small activation fee to the wallet address and claim your prize.
QR code visible. Link is partially cropped. Source account not visible.
```

### fraud_fake_grant__screenshot_ocr

- Mutation: Screenshot OCR
- Baseline action: high_confidence_escalation
- Mutated action: send_to_human_review
- Probability delta: -0.001
- Public label dropped: True
- Escaped review/label: False

```text
[Image OCR]
Screenshot text: Official Microsoft crypto grant for verified users. Send 0.05 BTC to validate identity and receive your bonus grant immediately.
QR code visible. Link is partially cropped. Source account not visible.
```

### fraud_wallet_drainer_airdrop__screenshot_ocr

- Mutation: Screenshot OCR
- Baseline action: high_confidence_escalation
- Mutated action: send_to_human_review
- Probability delta: -0.006
- Public label dropped: True
- Escaped review/label: False

```text
[Image OCR]
Screenshot text: Final airdrop window is open. Connect your wallet at secure-eth-airdrop.xyz now to claim free ETH before eligibility expires.
QR code visible. Link is partially cropped. Source account not visible.
```

### fraud_hyip_guaranteed_returns__screenshot_ocr

- Mutation: Screenshot OCR
- Baseline action: high_confidence_escalation
- Mutated action: send_to_human_review
- Probability delta: -0.012
- Public label dropped: True
- Escaped review/label: False

```text
[Image OCR]
Screenshot text: Private crypto pool now open. Guaranteed 300% monthly returns, risk-free, automated AI trading. Deposit USDT before midnight.
QR code visible. Link is partially cropped. Source account not visible.
```

### fraud_elon_multiplier__screenshot_ocr

- Mutation: Screenshot OCR
- Baseline action: high_confidence_escalation
- Mutated action: send_to_human_review
- Probability delta: -0.006
- Public label dropped: True
- Escaped review/label: False

```text
[Image OCR]
Screenshot text: Elon Musk official giveaway. Send 0.1 ETH to the verified wallet below and receive 1 ETH back instantly. Limited time.
QR code visible. Link is partially cropped. Source account not visible.
```

### fraud_fake_exchange_support__synonym_laundering

- Mutation: Synonym laundering
- Baseline action: apply_potential_crypto_fraud_label
- Mutated action: send_to_human_review
- Probability delta: -0.148
- Public label dropped: True
- Escaped review/label: False

```text
Coinbase support escalation: verify your vault address and transfer a small ETH fund so we can remove the account restriction.
```

## Standards Mapping

| Standard / Frame | Variants | Escapes | Downgrades |
| --- | ---: | ---: | ---: |
| MITRE ATLAS: evasion testing | 21 | 0 | 1 |
| MITRE ATLAS: robustness testing | 7 | 0 | 3 |
| NIST AI RMF Manage | 7 | 0 | 3 |
| NIST AI RMF Map | 14 | 0 | 7 |
| NIST AI RMF Measure | 21 | 0 | 4 |
| NIST CSF Detect | 14 | 0 | 0 |
| OWASP: multimodal content risk | 7 | 0 | 7 |
| OWASP: untrusted content handling | 7 | 0 | 0 |
| Santa Clara Integrity | 7 | 0 | 0 |
| Santa Clara Understandable Rules | 7 | 0 | 3 |

## Next Controls

- Add canonicalization before scoring: normalize leetspeak, defanged URLs, bracket-dot domains, and spaced scam keywords.
- Add OCR-specific review routing when source account, link target, or QR destination is missing.
- Add URL expansion and landing-page analysis before public enforcement.
- Track mutation failures as regression tests in CI before changing thresholds or model features.
