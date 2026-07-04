# LLM Evidence Adapter — Baseline vs Hosted-Model Comparison

Provider: **claude-fable-5 (cached 2026-07-03)** · 19 cases · generated 2026-07-04

- LLM expectation pass rate: **95%**
- Baseline expectation pass rate: **100%**
- Action agreement: **95%**
- Span faithfulness (same gate as deterministic extractor): **100%**

## Economics

- Baseline: $0 (CPU, <1 ms/post)
- LLM: $5-15 depending on model tier (700 in / 450 out tokens/post)
- Latency: 1-4 s per call vs <1 ms baseline

At 1M posts/day the LLM cannot be the first-pass filter on cost alone. The defensible architecture is baseline-first triage with LLM evidence extraction only on the review-queue slice (~5-20% of volume), which is exactly how this lab wires it.

## Per-case outcomes

| Case | Expected | Baseline | LLM | Agree |
| --- | --- | --- | --- | --- |
| fraud_elon_multiplier | public_label_candidate | public_label_candidate | public_label_candidate | yes |
| fraud_wallet_drainer_airdrop | public_label_candidate | public_label_candidate | public_label_candidate | yes |
| fraud_recovery_fee_advance | public_label_candidate | public_label_candidate | public_label_candidate | yes |
| fraud_hyip_guaranteed_returns | public_label_candidate | public_label_candidate | public_label_candidate | yes |
| fraud_fake_exchange_support | public_label_candidate | public_label_candidate | public_label_candidate | yes |
| fraud_promo_code_fee | public_label_candidate | public_label_candidate | public_label_candidate | yes |
| fraud_fake_grant | public_label_candidate | public_label_candidate | public_label_candidate | yes |
| fraud_dm_investment_mentor | public_label_candidate | public_label_candidate | public_label_candidate | yes |
| legit_coinbase_earnings | no_action | no_action | no_action | yes |
| legit_regulator_warning | no_action | no_action | no_action | yes |
| legit_academic_research | no_action | no_action | no_action | yes |
| legit_wallet_help | human_review | human_review | no_action ❌ | no |
| legit_satire_bitcoin_ceo | no_action | no_action | no_action | yes |
| legit_dev_wallet_bug | no_action | no_action | no_action | yes |
| legit_price_discussion | no_action | no_action | no_action | yes |
| ambiguous_airdrop_announcement | human_review | human_review | human_review | yes |
| ambiguous_recovery_service | human_review | human_review | human_review | yes |
| ambiguous_influencer_signal | human_review | human_review | human_review | yes |
| ambiguous_qr_image_ocr | human_review | human_review | human_review | yes |

## Interpretation

Where the two disagree, the interesting cases are stance cases: the baseline keys on WHAT vocabulary appears, the LLM on WHO is speaking and WHY. The error-analysis report shows the baseline's largest real false-positive class is skeptical third-party reportage — exactly the stance distinction an LLM reads natively. That, not aggregate accuracy on this small suite, is the argument for LLM assistance on the review slice. The one scored disagreement (legit_wallet_help: suite expects review, the model chose no-action to avoid burdening a help-seeker) is preserved rather than tuned away — it is a live policy question, and pretending the tools agree would hide it.
