# Error Analysis — What This System Gets Wrong

Generated 2026-07-26. 1 decision-level false positives, 0 full misses on the held-out test set; 6 of 9 authored hard cases still failing (published deliberately — see Decision Log 010).

## Decision-level false positives (held-out test set)

Legitimate posts that would reach label-candidate or escalation before a reviewer touches them. Reviewer confirmation is the control that keeps these from becoming user-visible harm.

### test-fp-165 — personal_solicitation_out_of_scope (score 0.62, high_confidence_escalation)

> "Can someone please send some BTC 💰 to my crypto wallet? 1KJLqaUxRLpC8UtR8HiQGFj1SmnFNKMCg6"

Begging for crypto is not an investment scam under this policy (no promised return, no fake opportunity). Wrong under this policy's definition even if another policy might cover spam or solicitation. Candidate fix: require a return-promise or opportunity claim before transfer-request evidence counts toward labeling.

## Full misses (fraud receiving no action)

None at the current operating point (recall 1.0 on this corpus — a fact that says as much about corpus size as about the model).

## Unsolved hard cases (standing red-team surface)

| Case | Category | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| unsolved-001 | warning_wrapper_evasion | send_to_human_review | no_label | known failure |
| unsolved-002 | doubt_language_evasion | send_to_human_review | no_label | known failure |
| unsolved-003 | recovery_testimonial | send_to_human_review | send_to_human_review | pass |
| unsolved-004 | multilingual_obfuscation | apply_potential_crypto_fraud_label | send_to_human_review | known failure |
| unsolved-005 | recruitment_surface | send_to_human_review | send_to_human_review | pass |
| unsolved-006 | off_text_evidence | send_to_human_review | no_label | known failure |
| unsolved-007 | soft_authority_insider | send_to_human_review | no_label | known failure |
| unsolved-008 | protective_bait | send_to_human_review | send_to_human_review | pass |
| guard-001 | protected_context_guard | no_label | no_label | pass |
| unsolved-009 | slow_burn_platform | send_to_human_review | no_label | known failure |

### Why each failure is still open

**unsolved-001 (warning_wrapper_evasion):** Adversary wraps a drainer lure in protective language. Protective-context suppression should not grant immunity when the same post contains a connect-wallet ask; the conflict should route to review. _Blind spot: Protective-context patterns currently suppress the public label without checking whether the speaker adds their own ask._

**unsolved-002 (doubt_language_evasion):** Testimonial-with-doubt is a documented scam format: the doubt markers are camouflage. Should route to review on doubling claim + DM funnel. _Blind spot: Doubt markers reduce risk scoring in exactly the way adversaries want._

**unsolved-004 (multilingual_obfuscation):** Spanish send-to-receive with leetspeak obfuscation of the guarantee keyword. Canonicalization plus Spanish rules should hold the label. _Blind spot: Leetspeak canonicalization coverage for non-English keywords is untested beyond this case._

**unsolved-006 (off_text_evidence):** The operative scam content lives in an image the text pipeline cannot see; the doubling promise in text should still carry it to review. _Blind spot: OCR evidence extraction is simulated only; image-borne asks are invisible._

**unsolved-007 (soft_authority_insider):** Unverifiable insider authority plus an advance fee. No brand name is dropped, so authority-misuse patterns keyed to named brands may not fire. _Blind spot: Authority detection is keyed to named entities; anonymous authority claims slip through._

**unsolved-009 (slow_burn_platform):** Serialized fake-platform promotion: each post individually mild, pattern lethal. Single-post review routing on repeated yield claims plus offer-to-share is the best available proxy until account-history enrichment exists. _Blind spot: No cross-post memory in the current pipeline; the campaign graph only clusters infrastructure, not serialized behavior by one account._

