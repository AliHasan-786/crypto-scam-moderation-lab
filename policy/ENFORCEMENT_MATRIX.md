# Enforcement Matrix — Crypto Investment Scams

Companion to the [Crypto Investment Scam Policy](CRYPTO_INVESTMENT_SCAM_POLICY.md) v2.0. Each row states the minimum evidence for each action, what first-detection versus repeat/campaign detection changes, and the appeal treatment.

**Severity scale:** S1 = highest harm (active theft mechanism), S3 = lower harm (deceptive promotion without a direct theft mechanism).

| Violation subtype | Severity | Minimum evidence for review | Minimum evidence for public label | Repeat / campaign escalation | Appealable |
| --- | --- | --- | --- | --- | --- |
| Send-to-receive ("doubling") scheme | S1 | Doubling structure detected | Doubling structure + wallet address or link from the speaker | Immediate high-confidence escalation; graph expansion on the receiving wallet | Yes |
| Wallet-drainer lure (connect/approve prompt) | S1 | Free-claim promise + connect-wallet instruction | Same + external unverified domain | Domain added to campaign graph; sibling posts auto-queued for review | Yes |
| Advance-fee recovery scam | S1 | Recovery offer + upfront-fee or DM-me structure | Recovery offer + fee ask from the speaker (not help-seeking) | Handle clustering; victim-targeting flag raises priority | Yes |
| Impersonation (exchange/brand/founder/support) | S1–S2 | Authority claim + any ask | Authority claim + transfer/credential/connection ask | Coordinated impersonation triggers incident-response evaluation (SEV2 criteria in the runbook) | Yes |
| Giveaway / airdrop fraud | S2 | Free-token claim + urgency or verification step | Free-token claim + transfer/connect requirement | Reused domain or wallet across ≥3 posts escalates the cluster | Yes |
| Guaranteed-return / HYIP / AI-bot promotion | S2 | Guaranteed or risk-free return claim | Guarantee + solicitation to deposit on the speaker's platform | Repeat promotion of the same platform clusters as a campaign | Yes |
| Pump group / insider-signal sales | S3 | Paid-access pitch to coordinated gains | Guaranteed-profit claim + payment/DM funnel | Cross-post handle reuse escalates | Yes |

## Non-violations mapped against lookalike violations

The rows below exist because these are the boundary cases reviewers actually face. They are covered by protected-context eval and calibration cases.

| Looks like | Actually is | Correct outcome |
| --- | --- | --- |
| "Connect your wallet" phrasing | Security warning telling users NOT to connect | No action; protective language check |
| Doubling language | News report or satire about doubling scams | No action; speaker-ask check |
| Recovery-service mention | Victim asking whether a recovery service is a scam | No action; route to help resources |
| High-APY discussion | Skeptical question about a platform's claims | No action or review if link present; never label |
| Airdrop announcement | Verifiable project's official airdrop with no fee/seed-phrase ask | No action; review if domain unverifiable |

## Action definitions

- **Human review:** queued to a reviewer with evidence panel; no user-visible effect; SLA target defined in ops metrics.
- **Public label:** "Potential Crypto Fraud" interstitial on the post after reviewer confirmation, with user notice and appeal link. Automated labeling without reviewer confirmation is not permitted at any confidence level (see Decision Log entry 004).
- **High-confidence escalation:** priority queue position, campaign-graph expansion, and incident-criteria evaluation. Not a separate user-visible action.
- **Account-level actions** (rate limits, feature restrictions, suspension) are out of scope for this lab and noted here only to mark the boundary: they would require multi-post evidence and human sign-off in a production system.
