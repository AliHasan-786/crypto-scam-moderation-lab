# Reviewer Calibration Guide

This guide turns the crypto-scam policy into an operational review workflow. It is designed for policy operations, quality, analyst, and reviewer-tooling roles.

## Review Goal

Apply the `Potential Crypto Fraud` label only when the post contains concrete scam evidence and does not clearly sit inside a protected or benign context.

The system has three operational outcomes:

- `public_label`: strong evidence supports a user-visible Potential Crypto Fraud label.
- `human_review`: suspicious or high-risk details exist, but context is incomplete enough that a public label could overreach.
- `no_label`: the content is legitimate, protective, satirical, technical, research-oriented, or too weak for action.

## Evidence That Supports Public Labeling

Strong evidence includes:

- requests to send BTC, ETH, SOL, USDT, or other crypto
- upfront fees or deposits
- wallet-connection pressure
- guaranteed, risk-free, doubled, or extreme returns
- suspicious airdrops, prize claims, promo codes, or giveaway language
- fake support, account restriction, or exchange impersonation
- suspicious domains, defanged links, shorteners, wallet/claim paths, or brand-impersonation domains
- urgency or scarcity that pressures immediate action

## Evidence That Should Suppress Public Labeling

Suppress public labels when the post is clearly:

- warning others about scams
- asking for help or verification
- market news or governance discussion
- developer/debugging discussion
- satire or parody
- research, journalism, education, or policy discussion

## When To Route To Human Review

Use human review when:

- OCR/source context is missing
- a link is cropped, shortened, redirected, or unverified
- the speaker intent is unclear
- the post asks whether something is legitimate
- the content is multilingual and the reviewer needs context
- enforcement would create a meaningful false-positive risk

## QA Dimensions

Calibration should score reviewers on:

- Policy accuracy: did the reviewer choose the expected action?
- Evidence grounding: did the notes cite concrete words, links, or entities?
- Context sensitivity: did the reviewer avoid labeling warnings, satire, research, or help-seeking?
- Severity judgment: did high-risk fraud receive faster escalation?
- Consistency: would another trained reviewer likely reach the same decision?

## Feedback Loop

Every reviewed case should be usable by at least one downstream process:

- policy clarification
- eval case creation
- model threshold review
- reviewer training
- campaign intelligence
- appeal handling
- transparency reporting
