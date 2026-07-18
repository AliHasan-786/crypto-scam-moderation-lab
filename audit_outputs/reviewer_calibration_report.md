# Reviewer Calibration Report

Generated: `2026-07-18T23:09:11.103025+00:00`

## Summary

- Calibration cases: **12**
- Public-label answer-key cases: **5**
- Human-review answer-key cases: **3**
- No-label answer-key cases: **4**
- Protected-context cases: **7**
- Multilingual cases: **2**
- URL/redirect/wallet-drainer cases: **4**

## Action Distribution

- `human_review`: 3
- `no_label`: 4
- `public_label`: 5

## QA Standards

- Reviewer must cite concrete evidence for public labels.
- Reviewer must identify protected context before applying public labels.
- Suspicious but incomplete cases should route to human review.
- Reviewer notes should be specific enough for appeal and QA review.
- Repeated calibration misses should become policy guidance or eval cases.

## Recommended QA Process

- Run calibration before reviewer launch and after policy updates.
- Score each reviewer against expected action, evidence quality, and context sensitivity.
- Review disagreement cases in group calibration.
- Promote common misses into evals and training examples.
- Track false-positive and false-negative themes over time.

## Calibration Cases

### calib_clear_wallet_drainer

- Expected action: `public_label`
- Expected decision: `fraud`
- Policy focus: `wallet_drainer`
- Severity: `high`
- Rationale: Airdrop lure, wallet connection request, suspicious domain, and urgency justify a public Potential Crypto Fraud label.

### calib_recovery_fee

- Expected action: `public_label`
- Expected decision: `fraud`
- Policy focus: `recovery_scam`
- Severity: `high`
- Rationale: Recovery service plus upfront crypto fee and certainty claims are classic fraud indicators.

### calib_consumer_warning

- Expected action: `no_label`
- Expected decision: `not_fraud`
- Policy focus: `consumer_warning`
- Severity: `low`
- Rationale: The post discusses scam indicators in a protective warning context and should not be labeled as promotion.

### calib_market_news

- Expected action: `no_label`
- Expected decision: `not_fraud`
- Policy focus: `market_news`
- Severity: `low`
- Rationale: Market/governance commentary with explicit no-link/no-claim context should suppress public enforcement.

### calib_spanish_wallet_lure

- Expected action: `public_label`
- Expected decision: `fraud`
- Policy focus: `multilingual_wallet_drainer`
- Severity: `high`
- Rationale: Spanish-language wallet-connection lure with suspicious brand/domain and urgency should be handled consistently.

### calib_spanish_help_seeking

- Expected action: `human_review`
- Expected decision: `needs_more_context`
- Policy focus: `multilingual_help_seeking`
- Severity: `medium`
- Rationale: Suspicious details are present, but the speaker appears to be asking for help rather than promoting the link.

### calib_fake_support_deposit

- Expected action: `public_label`
- Expected decision: `fraud`
- Policy focus: `support_impersonation`
- Severity: `high`
- Rationale: Exchange support impersonation plus deposit request is strong enforcement evidence.

### calib_developer_debugging

- Expected action: `no_label`
- Expected decision: `not_fraud`
- Policy focus: `developer_context`
- Severity: `low`
- Rationale: Developer/debugging context should suppress a public crypto-fraud label.

### calib_ocr_cropped_qr

- Expected action: `human_review`
- Expected decision: `needs_more_context`
- Policy focus: `ocr_source_ambiguity`
- Severity: `medium`
- Rationale: The content is suspicious, but missing source/link context makes human review safer than automatic public labeling.

### calib_shortener_prize

- Expected action: `public_label`
- Expected decision: `fraud`
- Policy focus: `shortener_giveaway`
- Severity: `high`
- Rationale: Prize claim, wallet language, shortener, and urgency together justify enforcement.

### calib_satire

- Expected action: `no_label`
- Expected decision: `not_fraud`
- Policy focus: `satire`
- Severity: `low`
- Rationale: The post uses scam-like language but clearly marks itself as satire.

### calib_redirect_mismatch

- Expected action: `human_review`
- Expected decision: `needs_more_context`
- Policy focus: `redirect_mismatch`
- Severity: `medium`
- Rationale: Redirect mismatch and unverified claim path should trigger review, not automatic public enforcement.
