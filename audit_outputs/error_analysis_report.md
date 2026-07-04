# Error Analysis — What This System Gets Wrong

Generated 2026-07-04. 8 decision-level false positives, 0 full misses on the held-out test set; 5 of 9 authored hard cases still failing (published deliberately — see Decision Log 010).

## Decision-level false positives (held-out test set)

Legitimate posts that would reach label-candidate or escalation before a reviewer touches them. Reviewer confirmation is the control that keeps these from becoming user-visible harm.

### test-fp-045 — skeptical_third_party_report (score 0.75, high_confidence_escalation)

> "A trading platform is offering 8% monthly returns on stablecoin deposits. They claim to be registered in Singapore, but I haven't verified the license."

The poster is describing an offer and signalling doubt — reporting, not promoting. The classifier keys on the described scam's features; the uncertain-review context patterns do not cover first-person reportage. This is the system's largest real false-positive class, and the reason reviewer confirmation is mandatory before any label (Decision Log 003/004). Candidate fix: a speaker-stance feature (describing vs. soliciting); risk: scammers adopting doubt language as camouflage — see unsolved-002.

### test-fp-132 — skeptical_third_party_report (score 0.57, apply_potential_crypto_fraud_label)

> "Someone DM'd me about a private crypto investment opportunity. They claim to have insider information about an upcoming token launch, but want a $500 'membership fee.'"

The poster is describing an offer and signalling doubt — reporting, not promoting. The classifier keys on the described scam's features; the uncertain-review context patterns do not cover first-person reportage. This is the system's largest real false-positive class, and the reason reviewer confirmation is mandatory before any label (Decision Log 003/004). Candidate fix: a speaker-stance feature (describing vs. soliciting); risk: scammers adopting doubt language as camouflage — see unsolved-002.

### test-fp-135 — skeptical_third_party_report (score 0.67, high_confidence_escalation)

> "I saw an ad for a platform offering 18% APY on Bitcoin deposits. They claim to be licensed in the Cayman Islands, but I haven't verified the license."

The poster is describing an offer and signalling doubt — reporting, not promoting. The classifier keys on the described scam's features; the uncertain-review context patterns do not cover first-person reportage. This is the system's largest real false-positive class, and the reason reviewer confirmation is mandatory before any label (Decision Log 003/004). Candidate fix: a speaker-stance feature (describing vs. soliciting); risk: scammers adopting doubt language as camouflage — see unsolved-002.

### test-fp-136 — skeptical_third_party_report (score 0.62, high_confidence_escalation)

> "A friend shared a link to a 'guaranteed profit' arbitrage opportunity. The concept makes sense, but the website asks for wallet connection immediately."

The poster is describing an offer and signalling doubt — reporting, not promoting. The classifier keys on the described scam's features; the uncertain-review context patterns do not cover first-person reportage. This is the system's largest real false-positive class, and the reason reviewer confirmation is mandatory before any label (Decision Log 003/004). Candidate fix: a speaker-stance feature (describing vs. soliciting); risk: scammers adopting doubt language as camouflage — see unsolved-002.

### test-fp-144 — skeptical_third_party_report (score 0.77, high_confidence_escalation)

> "A platform claims to offer 'insured' crypto deposits with 10% monthly returns. The insurance provider is mentioned but I can't find their official website."

The poster is describing an offer and signalling doubt — reporting, not promoting. The classifier keys on the described scam's features; the uncertain-review context patterns do not cover first-person reportage. This is the system's largest real false-positive class, and the reason reviewer confirmation is mandatory before any label (Decision Log 003/004). Candidate fix: a speaker-stance feature (describing vs. soliciting); risk: scammers adopting doubt language as camouflage — see unsolved-002.

### test-fp-146 — skeptical_third_party_report (score 0.70, high_confidence_escalation)

> "A crypto investment fund is accepting new investors with a $10K minimum. They claim 80% annual returns and have a professional website, but no regulatory filings visible."

The poster is describing an offer and signalling doubt — reporting, not promoting. The classifier keys on the described scam's features; the uncertain-review context patterns do not cover first-person reportage. This is the system's largest real false-positive class, and the reason reviewer confirmation is mandatory before any label (Decision Log 003/004). Candidate fix: a speaker-stance feature (describing vs. soliciting); risk: scammers adopting doubt language as camouflage — see unsolved-002.

### test-fp-165 — personal_solicitation_out_of_scope (score 0.62, high_confidence_escalation)

> "Can someone please send some BTC 💰 to my crypto wallet? 1KJLqaUxRLpC8UtR8HiQGFj1SmnFNKMCg6"

Begging for crypto is not an investment scam under this policy (no promised return, no fake opportunity). Wrong under this policy's definition even if another policy might cover spam or solicitation. Candidate fix: require a return-promise or opportunity claim before transfer-request evidence counts toward labeling.

### test-fp-167 — naive_question (score 0.60, apply_potential_crypto_fraud_label)

> "How do I get free BTC?"

A short curiosity question tripping free-crypto patterns. Labeling a question as fraud is a category error; at most this deserves a safety resource surface. Candidate fix: interrogative-form dampening.

## Full misses (fraud receiving no action)

None at the current operating point (recall 1.0 on this corpus — a fact that says as much about corpus size as about the model).

## Unsolved hard cases (standing red-team surface)

| Case | Category | Expected | Actual | Status |
| --- | --- | --- | --- | --- |
| unsolved-001 | warning_wrapper_evasion | send_to_human_review | no_label | known failure |
| unsolved-002 | doubt_language_evasion | send_to_human_review | no_label | known failure |
| unsolved-003 | recovery_testimonial | send_to_human_review | send_to_human_review | pass |
| unsolved-004 | multilingual_obfuscation | apply_potential_crypto_fraud_label | high_confidence_escalation | pass |
| unsolved-005 | recruitment_surface | send_to_human_review | send_to_human_review | pass |
| unsolved-006 | off_text_evidence | send_to_human_review | no_label | known failure |
| unsolved-007 | soft_authority_insider | send_to_human_review | no_label | known failure |
| unsolved-008 | protective_bait | send_to_human_review | send_to_human_review | pass |
| guard-001 | protected_context_guard | no_label | no_label | pass |
| unsolved-009 | slow_burn_platform | send_to_human_review | no_label | known failure |

### Why each failure is still open

**unsolved-001 (warning_wrapper_evasion):** Adversary wraps a drainer lure in protective language. Protective-context suppression should not grant immunity when the same post contains a connect-wallet ask; the conflict should route to review. _Blind spot: Protective-context patterns currently suppress the public label without checking whether the speaker adds their own ask._

**unsolved-002 (doubt_language_evasion):** Testimonial-with-doubt is a documented scam format: the doubt markers are camouflage. Should route to review on doubling claim + DM funnel. _Blind spot: Doubt markers reduce risk scoring in exactly the way adversaries want._

**unsolved-006 (off_text_evidence):** The operative scam content lives in an image the text pipeline cannot see; the doubling promise in text should still carry it to review. _Blind spot: OCR evidence extraction is simulated only; image-borne asks are invisible._

**unsolved-007 (soft_authority_insider):** Unverifiable insider authority plus an advance fee. No brand name is dropped, so authority-misuse patterns keyed to named brands may not fire. _Blind spot: Authority detection is keyed to named entities; anonymous authority claims slip through._

**unsolved-009 (slow_burn_platform):** Serialized fake-platform promotion: each post individually mild, pattern lethal. Single-post review routing on repeated yield claims plus offer-to-share is the best available proxy until account-history enrichment exists. _Blind spot: No cross-post memory in the current pipeline; the campaign graph only clusters infrastructure, not serialized behavior by one account._

