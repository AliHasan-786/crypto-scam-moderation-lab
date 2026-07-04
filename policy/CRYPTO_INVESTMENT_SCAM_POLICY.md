# Crypto Investment Scam Policy

**Version:** 2.0
**Status:** Reference implementation for the Crypto Scam Moderation Lab
**Applies to:** Public posts on Bluesky-style text-first social platforms
**Companion documents:** [Enforcement Matrix](ENFORCEMENT_MATRIX.md) · [Decision Log](DECISION_LOG.md) · [Metrics Definitions](../ops_analytics/METRICS_DEFINITIONS.md) · [Threat Landscape](../threat_landscape/THREAT_LANDSCAPE.md)

> This is a portfolio reference policy written in the format a platform policy team would publish internally. It is enforced by the lab's detection and review pipeline, not by any live platform.

---

## 1. Purpose and principles

This policy defines when crypto-related content constitutes an investment scam that warrants platform intervention, and — equally important — when it does not. It is built on four principles:

1. **Financial speech is legitimate speech.** Crypto news, education, analysis, criticism, satire, and help-seeking are not violations, even when they use the same vocabulary scammers use.
2. **Public accusations require strong evidence.** A visible "Potential Crypto Fraud" label is itself a harm if wrong. Public labels demand a higher evidence bar than routing to human review.
3. **Uncertainty routes to humans.** When intent, source, or context cannot be established from available signals, the correct system action is human review — not enforcement and not inaction.
4. **Every enforcement action is explainable and appealable.** Users receive a notice stating what rule was matched and what evidence supported it, and can appeal.

## 2. Definitions

**Investment scam:** content that persuades people to send money or crypto assets to an illegitimate or nonexistent opportunity through promises of easy returns, low or no risk, fabricated authority, or urgent limited access.

**In-scope harm types** (see the [Enforcement Matrix](ENFORCEMENT_MATRIX.md) for subtype-level treatment):

- **Giveaway / airdrop fraud** — free-token claims requiring a "verification" transfer, wallet connection, or fee.
- **Send-to-receive ("doubling") schemes** — send X, receive 2X, typically with impersonated authority.
- **Guaranteed-return / HYIP promotion** — risk-free, fixed, or implausibly high returns; AI-bot trading guarantees.
- **Impersonation of exchanges, brands, founders, or support** — fake official accounts, support escalation lures, account-restriction phishing.
- **Advance-fee recovery scams** — "we can recover your stolen funds for an upfront fee," which re-victimizes prior victims.
- **Pump groups and insider-signal sales** — paid access to "guaranteed" coordinated price manipulation.
- **Wallet-drainer lures** — any prompt to connect a wallet or approve a transaction on an unverified external site.

**Out of scope for this policy** (handled by other policies in a real platform): romance-scam grooming without an investment ask, general phishing without a crypto element, securities-law compliance questions about legitimate projects, and market commentary however irresponsible.

## 3. Protected contexts (never publicly labeled)

The following contexts suppress public labeling even when scam vocabulary is present. This list is enforced in code (`protected context` features in the classifier and rubric) and tested by dedicated eval cases:

| Context | Example | System behavior |
| --- | --- | --- |
| Warnings and PSAs | "Do NOT connect your wallet to this airdrop site — it's a drainer." | No label. Never route the warner to enforcement. |
| News and reporting | "SEC charges promoter of a fake BTC doubling scheme." | No label. |
| Research and education | "Here's how send-to-receive scams manipulate urgency…" | No label. |
| Satire and jokes | "Send me 1 imaginary DogeMoonCoin and I'll send back 2, trust me bro." | No label; satire markers checked for real-fund asks. |
| Developer/debugging content | "Testing my faucet contract on testnet, sending 0.1 test ETH." | No label. |
| Victim help-seeking | "I think I got scammed by a recovery service, what do I do?" | No label; route to support resources, never enforcement. |

Ambiguity between protected context and violation (e.g., a "warning" that itself links the scam site) routes to human review.

## 4. Evidence standards

Detection signals are tiered by probative weight:

**Strong (can support a public label in combination):** a direct transfer request from the speaker; wallet-connection instruction tied to a free-claim promise; send-to-receive structure; impersonated authority plus an ask; known scam infrastructure (domain/wallet reuse across the campaign graph).

**Moderate (support review, not labeling alone):** guaranteed-return language; urgency and scarcity framing; promo-code/airdrop vocabulary; celebrity name-drops without an ask.

**Weak (never actionable alone):** crypto vocabulary, emoji density, hashtags, excitement, poor grammar, links to unknown domains.

A public label requires at least one strong signal with no protected-context indicator. Review requires a moderate aggregate score or unresolved context. Single weak signals produce no action.

## 5. Enforcement tiers

The pipeline maps calibrated model scores plus rubric evidence to four actions. Operating thresholds and the reasoning behind them are recorded in the [Decision Log](DECISION_LOG.md).

| Tier | Trigger (current operating point) | Action |
| --- | --- | --- |
| **No action** | Score < 0.40 and no strong signal | Content remains untouched. |
| **Human review** | Score ≥ 0.40 (policy floor), or strong-signal/context conflict | Queued for reviewer decision; no user-visible effect. |
| **Public label candidate** | Score ≥ 0.54 and strong evidence and no protected context | "Potential Crypto Fraud" label pending reviewer confirmation; user notice + appeal path. |
| **High-confidence escalation** | Score ≥ 0.61 plus campaign-infrastructure evidence | Priority review, campaign-graph expansion, incident evaluation. |

No tier in this lab publishes actions to any live platform; the public demo is read-only by design.

## 6. Appeals and reversals

Every public label ships with a notice naming the matched rule and evidence category. Appeals follow the flows in [`governance/appeal_scenarios.json`](../governance/appeal_scenarios.json): a reviewer other than the original decision-maker re-evaluates with the appellant's context, reversals are recorded, and reversal categories feed back into eval cases and this policy's revision cycle. Documented reversal drivers so far: consumer warnings misread as solicitations, and satire misread as an ask.

## 7. Measurement

This policy's health is tracked by the metrics defined in [Metrics Definitions](../ops_analytics/METRICS_DEFINITIONS.md): public-label precision (primary guardrail), review-or-label recall (primary safety net), protected-context false-positive rate, appeal overturn rate, mutation retention, and time-to-action. Aggregate F1 is reported but is never the optimization target.

## 8. Change management

Policy changes require: a decision-log entry with the tradeoff accepted, new or updated eval cases encoding the boundary, and a passing release gate. The policy version increments when the enforcement matrix or protected-context list changes.

## 9. Known limitations

The training corpus is small and mostly English; Spanish coverage exists in rules and hardening evals but is thin. OCR of screenshot scams and live URL resolution are simulated. Off-platform context (DMs, landing pages) is out of reach, which is precisely why the review tier exists.
