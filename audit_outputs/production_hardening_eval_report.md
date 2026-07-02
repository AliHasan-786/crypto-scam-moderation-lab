# Production Hardening Eval Report

This is an authored production-hardening suite. It is not an untouched benchmark; it probes known deployment risks such as canonicalization, URL evidence, OCR ambiguity, multilingual phrasing, and protected-context false positives.

## Summary

- Cases: 12
- Expectation pass rate: 100.0%
- Fraud public-label recall: 100.0%
- Review-or-label recall for expected review cases: 100.0%
- Legitimate no-public-label rate: 100.0%
- Ambiguous review rate: 100.0%
- Canonicalization applied in: 9 cases
- Cases with URL evidence: 7

## Dimensions

- Brand Impersonation: 2/2 passed (100.0%)
- Canonicalization: 2/2 passed (100.0%)
- Defanged Url: 3/3 passed (100.0%)
- Developer Context: 1/1 passed (100.0%)
- False Positive Control: 4/4 passed (100.0%)
- Giveaway: 1/1 passed (100.0%)
- Leetspeak: 1/1 passed (100.0%)
- Market News: 1/1 passed (100.0%)
- Missing Context: 2/2 passed (100.0%)
- Multilingual: 3/3 passed (100.0%)
- Ocr: 1/1 passed (100.0%)
- Protected Context: 2/2 passed (100.0%)
- Redirect Mismatch: 1/1 passed (100.0%)
- Review Routing: 3/3 passed (100.0%)
- Shortener: 1/1 passed (100.0%)
- Support Impersonation: 1/1 passed (100.0%)
- Url Evidence: 4/4 passed (100.0%)
- Wallet Connection: 1/1 passed (100.0%)
- Wallet Drainer: 1/1 passed (100.0%)

## URL Evidence

- hardening_spaced_wallet_defanged_airdrop: `secure-airdrop.xyz` risk 0.62; Campaign Keyword Domain, Defanged Url, Suspicious Tld, Wallet Or Claim Path
- hardening_defanged_research_warning: `secure-airdrop.xyz` risk 0.62; Campaign Keyword Domain, Defanged Url, Suspicious Tld, Wallet Or Claim Path
- hardening_spanish_wallet_airdrop: `metamask-bono.top` risk 0.56; Brand Impersonation Domain, Defanged Url, Suspicious Tld
- hardening_brand_impersonation_domain: `metamask-security.top` risk 0.56; Brand Impersonation Domain, Defanged Url, Suspicious Tld
- hardening_developer_wallet_debug: `dev-wallet.local` risk 0.50; Campaign Keyword Domain, Defanged Url, Wallet Or Claim Path
- hardening_redirect_mismatch_review: `project-update.click` risk 0.44; Defanged Url, Suspicious Tld, Wallet Or Claim Path
- hardening_shortener_claim_lure: `bit.ly` risk 0.34; Url Shortener, Wallet Or Claim Path

## Top Failures

- No expectation failures.

## Cases

- hardening_spaced_wallet_defanged_airdrop: High Confidence Escalation; passed=True; dimensions=Canonicalization, Defanged Url, Wallet Drainer
- hardening_leetspeak_support_deposit: Apply Potential Crypto Fraud Label; passed=True; dimensions=Canonicalization, Leetspeak, Support Impersonation
- hardening_spanish_wallet_airdrop: High Confidence Escalation; passed=True; dimensions=Multilingual, Defanged Url, Brand Impersonation
- hardening_shortener_claim_lure: High Confidence Escalation; passed=True; dimensions=Url Evidence, Shortener, Giveaway
- hardening_brand_impersonation_domain: Apply Potential Crypto Fraud Label; passed=True; dimensions=Url Evidence, Brand Impersonation, Wallet Connection
- hardening_ocr_cropped_qr_review: Send To Human Review; passed=True; dimensions=Ocr, Missing Context, Review Routing
- hardening_spanish_airdrop_question_review: Send To Human Review; passed=True; dimensions=Multilingual, Missing Context, Review Routing
- hardening_defanged_research_warning: No Label; passed=True; dimensions=Protected Context, Defanged Url, False Positive Control
- hardening_spanish_consumer_warning: No Label; passed=True; dimensions=Multilingual, Protected Context, False Positive Control
- hardening_developer_wallet_debug: No Label; passed=True; dimensions=Developer Context, Url Evidence, False Positive Control
- hardening_market_news_airdrop: No Label; passed=True; dimensions=Market News, False Positive Control
- hardening_redirect_mismatch_review: Send To Human Review; passed=True; dimensions=Url Evidence, Redirect Mismatch, Review Routing
