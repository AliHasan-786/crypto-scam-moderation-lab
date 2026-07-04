# Governance And Transparency Report

Generated: 2026-07-04T02:16:03.981609+00:00

## Summary

- Local queue candidates: 5
- Reviewed or triaged: 3
- Actioned in queue: 1
- Authored appeal scenarios: 4
- Authored appeal reversal rate: 50.0%
- Automation-assisted queue rate: 100.0%
- Standards average score: 0.914

Interpretation: this report separates local operational metrics from authored appeal scenarios. The authored scenarios demonstrate due process, notice quality, and reversal handling without publishing or storing live platform user content.

## Queue Snapshot

- dismissed: 1
- escalated: 1
- new: 2
- review: 1

## Appeal Scenarios

### Consumer warning false positive

- Initial action: Potential Crypto Fraud label
- Appeal claim: The post is warning people about scams, not promoting one.
- Outcome: reversed
- User notice: We removed the Potential Crypto Fraud label after review. Your post appears to warn others about scam behavior rather than request funds.

### Satire mistaken for solicitation

- Initial action: Potential Crypto Fraud label
- Appeal claim: The post is an obvious joke using imaginary assets.
- Outcome: reversed
- User notice: We removed the label because the post is clear satire and does not request real funds.

### Wallet-drainer airdrop appeal

- Initial action: Potential Crypto Fraud label
- Appeal claim: The claim page is a legitimate promotion.
- Outcome: upheld
- User notice: After review, the label remains because the post asks users to connect a wallet through an unverified airdrop claim.

### Recovery-service ambiguity

- Initial action: Sent to human review
- Appeal claim: The post asks for advice and should not be publicly labeled.
- Outcome: clarification_sent
- User notice: No public label was applied. We routed the post to review because recovery-service claims can be high-risk and context-dependent.

## Notice Templates

### Potential Crypto Fraud label notice

- Trigger: Reviewer confirms concrete scam evidence.
- Body: We added a Potential Crypto Fraud label because the post appears to request crypto, wallet connection, or payment using scam-like claims. You can appeal if context is missing.

### Escalation notice

- Trigger: High-risk wallet, domain, or impersonation evidence requires deeper review.
- Body: This post was escalated for additional review because it combines high-risk crypto-scam signals such as wallet requests, impersonation, urgency, or repeated campaign infrastructure.

### Appeal received notice

- Trigger: A user challenges a label or moderation decision.
- Body: We received your appeal. A reviewer will check the original evidence, your added context, and whether the post falls into a protected context such as warning, research, satire, or help-seeking.

### Reversal notice

- Trigger: Reviewer finds the original action was not warranted.
- Body: We removed the label after review. The post does not meet the Potential Crypto Fraud standard under the available context.

## Standards Scorecard

- Santa Clara Principles / Clear public rule and boundary examples: implemented (1.00)
- Santa Clara Principles / Appeal path and reversal tracking: implemented (0.90)
- NIST AI RMF Measure / Measure false positives, ambiguity routing, and reviewer-action distribution: implemented (1.00)
- NIST AI RMF Manage / Route uncertainty to humans before public enforcement: implemented (0.95)
- NIST CSF 2.0 / Detect scam campaigns and respond through review/escalation: implemented (0.85)
- OWASP LLM / Agentic AI / Constrain LLM output to evidence assistance, not autonomous action: implemented (0.95)
- Trust & Safety Operations / Limit public demo data and keep live samples local: partial (0.75)

## Caveat

Operational queue metrics come from the local SQLite review store. Appeal examples are authored, sanitized portfolio scenarios that exercise notice, appeal, and reversal flows without using live user data.
