# Trust & Safety Ops Analytics Report

Generated: `2026-07-18T06:23:52.936071+00:00`

## Executive Summary

- Total queue items: **5**
- Reviewed items: **3**
- Unreviewed backlog: **2**
- Review coverage: **60.0%**
- Action rate: **20.0%**
- Dismissal rate among reviewed items: **33.3%**
- Total observations after duplicate refreshes: **8**

## Status Counts

- `new`: 2
- `dismissed`: 1
- `escalated`: 1
- `review`: 1

## Reviewer Decisions

- `unreviewed`: 2
- `fraud`: 1
- `needs_more_context`: 1
- `not_fraud`: 1

## Action Tiers

- `high_confidence_escalation`: 3 items, avg probability 0.754
- `no_label`: 1 items, avg probability 0.7467
- `send_to_human_review`: 1 items, avg probability 0.2579

## Backlog Candidates

- `high_confidence_escalation` / p=0.7593: Tesla crypto event support says deposits to 0x5afe00000000000000000000000000000000feed are required before the bonus release fee clears.
- `high_confidence_escalation` / p=0.6254: Verified BTC rewards round is closing. Claim at secure-btc-airdrop[.]xyz and connect wallet before the final warning.

## False-Positive Candidates

- `not_fraud` / p=0.7467: Reminder: do not send crypto to people promising guaranteed returns. Social media investment scams are common.

## Entity Leads

- `wallet` `0x5afe00000000000000000000000000000000feed`: 2 linked items, max risk 0.92
- `risk_phrase` `connect_wallet`: 2 linked items, max risk 0.9
- `risk_phrase` `airdrop_claim`: 2 linked items, max risk 0.76
- `risk_phrase` `limited_time`: 2 linked items, max risk 0.68
- `domain` `secure-btc-airdrop.xyz`: 2 linked items, max risk 0.58
- `brand` `bitcoin`: 2 linked items, max risk 0.18
- `risk_phrase` `send_crypto`: 1 linked items, max risk 0.82
- `risk_phrase` `guaranteed_returns`: 1 linked items, max risk 0.78
- `risk_phrase` `processing_fee`: 1 linked items, max risk 0.74
- `risk_phrase` `recovery_service`: 1 linked items, max risk 0.7
- `actor` `btc-claims-demo.bsky.social`: 1 linked items, max risk 0.2
- `actor` `btc-rewards-demo.bsky.social`: 1 linked items, max risk 0.2

## Operational Questions

- SQL-readable queue health and reviewer decision metrics.
- False-positive and backlog examples for policy review.
- Entity leaderboard for fraud-intelligence and campaign triage.
- Event history for auditability and process improvement.

## Analyst Notes

- Backlog exists; prioritize unresolved items by action tier, probability, duplicate count, and shared entities.
- Dismissed/not-fraud cases should feed policy clarification and false-positive evals.
- Repeated entities are useful campaign leads, but should not trigger enforcement without content and context review.
- Reviewer decisions create an active-learning and QA feedback loop.
